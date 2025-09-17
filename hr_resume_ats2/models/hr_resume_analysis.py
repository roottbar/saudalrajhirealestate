# -*- coding: utf-8 -*-

import base64
import io
import json
import logging
import re
from datetime import datetime

try:
    import PyPDF2
    import docx
    import nltk
    import textstat
    import requests
except ImportError:
    PyPDF2 = None
    docx = None
    nltk = None
    textstat = None
    requests = None

# Alternative PDF libraries for fallback
try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    pypdf = None
    PYPDF_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    pdfplumber = None
    PDFPLUMBER_AVAILABLE = False

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class HrResumeAnalysis(models.Model):
    _name = 'hr.resume.analysis'
    _description = 'Resume Analysis using ATS System'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # Basic Information
    name = fields.Char('Analysis Name', required=True, tracking=True)
    candidate_name = fields.Char('Candidate Name', tracking=True)
    candidate_email = fields.Char('Email', tracking=True)
    candidate_phone = fields.Char('Phone', tracking=True)
    
    # Resume File
    resume_file = fields.Binary('Resume File', required=True, tracking=True)
    resume_filename = fields.Char('Resume Filename')
    resume_text = fields.Text('Extracted Resume Text', readonly=True)
    
    # Job Position
    job_position_id = fields.Many2one('hr.job.position', 'Target Job Position', required=True, tracking=True)
    job_description = fields.Html('Job Description', related='job_position_id.description', readonly=True)
    
    # Analysis Results
    overall_score = fields.Float('Overall Score (%)', readonly=True, tracking=True)
    ats_compatibility_score = fields.Float('ATS Compatibility Score (%)', readonly=True)
    skills_match_score = fields.Float('Skills Match Score (%)', readonly=True)
    experience_score = fields.Float('Experience Score (%)', readonly=True)
    education_score = fields.Float('Education Score (%)', readonly=True)
    keywords_score = fields.Float('Keywords Score (%)', readonly=True)
    
    # Detailed Analysis
    analysis_summary = fields.Html('Analysis Summary', readonly=True)
    strengths = fields.Text('Strengths', readonly=True)
    weaknesses = fields.Text('Areas for Improvement', readonly=True)
    recommendations = fields.Text('Recommendations', readonly=True)
    missing_keywords = fields.Text('Missing Keywords', readonly=True)
    
    # Skills Analysis
    found_skills = fields.Text('Found Skills', readonly=True)
    missing_skills = fields.Text('Missing Skills', readonly=True)
    skill_ids = fields.One2many('hr.resume.skill', 'resume_analysis_id', 'Skills Analysis')
    
    # Experience Analysis
    total_experience_years = fields.Float('Total Experience (Years)', readonly=True)
    relevant_experience_years = fields.Float('Relevant Experience (Years)', readonly=True)
    experience_ids = fields.One2many('hr.resume.experience', 'resume_analysis_id', 'Experience Analysis')
    
    # Education Analysis
    education_level = fields.Selection([
        ('high_school', 'High School'),
        ('diploma', 'Diploma'),
        ('bachelor', 'Bachelor Degree'),
        ('master', 'Master Degree'),
        ('phd', 'PhD'),
        ('other', 'Other')
    ], 'Education Level', readonly=True)
    education_ids = fields.One2many('hr.resume.education', 'resume_analysis_id', 'Education Analysis')
    
    # Status and Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('analyzing', 'Analyzing'),
        ('completed', 'Analysis Completed'),
        ('failed', 'Analysis Failed')
    ], 'Status', default='draft', tracking=True)
    
    # AI Analysis Settings
    ai_provider = fields.Selection([
        ('openai', 'OpenAI GPT'),
        ('google', 'Google AI'),
        ('local', 'Local Analysis')
    ], 'AI Provider', default='local')
    
    # Timestamps
    analysis_date = fields.Datetime('Analysis Date', readonly=True)
    analysis_duration = fields.Float('Analysis Duration (seconds)', readonly=True)
    
    # Company and User
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', 'Analyzed By', default=lambda self: self.env.user)
    
    @api.model
    def create(self, vals):
        if 'name' not in vals or not vals['name']:
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.resume.analysis') or _('New Analysis')
        return super(HrResumeAnalysis, self).create(vals)
    
    @api.onchange('resume_file')
    def _onchange_resume_file(self):
        """Extract text from uploaded resume file"""
        if self.resume_file and self.resume_filename:
            try:
                _logger.info(f"Processing resume file: {self.resume_filename}")
                self.resume_text = self._extract_text_from_file()
                self._extract_basic_info()
                _logger.info(f"Successfully processed resume file: {self.resume_filename}")
            except UserError:
                # Re-raise UserError as-is (these have user-friendly messages)
                raise
            except Exception as e:
                _logger.error(f"Unexpected error extracting text from resume '{self.resume_filename}': {str(e)}")
                _logger.error(f"Error type: {type(e).__name__}")
                # Provide more specific error message
                if "PyPDF2" in str(e):
                    raise UserError(_("PDF processing library error. Please contact system administrator."))
                elif "docx" in str(e):
                    raise UserError(_("Word document processing error. Please ensure it's a valid Word document."))
                else:
                    raise UserError(_("Error processing resume file '%s'. Please ensure it's a valid PDF or Word document. Error: %s") % (self.resume_filename, str(e)))
    
    def _extract_text_from_file(self):
        """Extract text from PDF or Word document"""
        if not self.resume_file:
            return ''
        
        try:
            file_data = base64.b64decode(self.resume_file)
        except Exception as e:
            _logger.error(f"Error decoding file data: {str(e)}")
            raise UserError(_("Invalid file data. Please upload a valid file."))
        
        if not self.resume_filename:
            raise UserError(_("File name is required. Please upload the file again."))
            
        filename = self.resume_filename.lower()
        
        # Check file size (max 10MB)
        if len(file_data) > 10 * 1024 * 1024:
            raise UserError(_("File size too large. Please upload a file smaller than 10MB."))
        
        # Check if file data is not empty
        if len(file_data) == 0:
            raise UserError(_("Empty file detected. Please upload a valid file."))
        
        if filename.endswith('.pdf'):
            return self._extract_text_from_pdf(file_data)
        elif filename.endswith(('.doc', '.docx')):
            return self._extract_text_from_word(file_data)
        else:
            raise UserError(_("Unsupported file format. Please upload PDF or Word document."))
    
    def _extract_text_from_pdf(self, file_data):
        """Extract text from PDF file with fallback options"""
        # Check if file starts with PDF header
        if not file_data.startswith(b'%PDF'):
            _logger.error(f"Invalid PDF header. First 10 bytes: {file_data[:10]}")
            raise UserError(_("Invalid PDF file format. Please ensure you're uploading a valid PDF file."))
        
        _logger.info(f"Starting PDF processing. File size: {len(file_data)} bytes")
        
        # Try PyPDF2 first
        if PyPDF2:
            try:
                return self._extract_with_pypdf2(file_data)
            except Exception as e:
                _logger.warning(f"PyPDF2 failed: {str(e)}. Trying alternative methods...")
        
        # Try pypdf as fallback
        if PYPDF_AVAILABLE:
            try:
                return self._extract_with_pypdf(file_data)
            except Exception as e:
                _logger.warning(f"pypdf failed: {str(e)}. Trying next method...")
        
        # Try pdfplumber as last resort
        if PDFPLUMBER_AVAILABLE:
            try:
                return self._extract_with_pdfplumber(file_data)
            except Exception as e:
                _logger.warning(f"pdfplumber failed: {str(e)}")
        
        # If all methods fail
        if not PyPDF2 and not PYPDF_AVAILABLE and not PDFPLUMBER_AVAILABLE:
            raise UserError(_("No PDF processing library is available. Please install PyPDF2, pypdf, or pdfplumber."))
        else:
            raise UserError(_("Failed to extract text from PDF using all available methods. The file might be corrupted, image-based, or in an unsupported format."))
    
    def _extract_with_pypdf2(self, file_data):
        """Extract text using PyPDF2 library"""
        pdf_file = io.BytesIO(file_data)
        
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            _logger.info(f"PyPDF2 reader created successfully. Number of pages: {len(pdf_reader.pages)}")
        except Exception as reader_error:
            _logger.error(f"Failed to create PyPDF2 reader: {str(reader_error)}")
            raise UserError(_("Failed to read PDF file with PyPDF2. The file might be corrupted or in an unsupported format."))
        
        # Check if PDF is encrypted
        if pdf_reader.is_encrypted:
            _logger.warning("PDF file is encrypted")
            raise UserError(_("PDF file is password protected. Please upload an unprotected PDF file."))
        
        # Check if PDF has pages
        if len(pdf_reader.pages) == 0:
            _logger.error("PDF file has no pages")
            raise UserError(_("PDF file has no pages. Please upload a valid PDF file."))
        
        text = ''
        successful_pages = 0
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text += page_text + '\n'
                    successful_pages += 1
                    _logger.debug(f"Successfully extracted text from page {page_num + 1} with PyPDF2")
                else:
                    _logger.warning(f"No text found on page {page_num + 1} with PyPDF2")
            except Exception as page_error:
                _logger.warning(f"Error extracting text from page {page_num + 1} with PyPDF2: {str(page_error)}")
                continue
        
        _logger.info(f"PyPDF2 extraction completed. Successful pages: {successful_pages}/{len(pdf_reader.pages)}")
        
        extracted_text = text.strip()
        if not extracted_text:
            raise UserError(_("No text could be extracted from the PDF using PyPDF2. Trying alternative methods..."))
        
        _logger.info(f"Successfully extracted {len(extracted_text)} characters from PDF using PyPDF2")
        return extracted_text
    
    def _extract_with_pypdf(self, file_data):
        """Extract text using pypdf library"""
        pdf_file = io.BytesIO(file_data)
        
        try:
            pdf_reader = pypdf.PdfReader(pdf_file)
            _logger.info(f"pypdf reader created successfully. Number of pages: {len(pdf_reader.pages)}")
        except Exception as reader_error:
            _logger.error(f"Failed to create pypdf reader: {str(reader_error)}")
            raise
        
        # Check if PDF is encrypted
        if pdf_reader.is_encrypted:
            _logger.warning("PDF file is encrypted (pypdf)")
            raise UserError(_("PDF file is password protected. Please upload an unprotected PDF file."))
        
        text = ''
        successful_pages = 0
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text += page_text + '\n'
                    successful_pages += 1
                    _logger.debug(f"Successfully extracted text from page {page_num + 1} with pypdf")
            except Exception as page_error:
                _logger.warning(f"Error extracting text from page {page_num + 1} with pypdf: {str(page_error)}")
                continue
        
        _logger.info(f"pypdf extraction completed. Successful pages: {successful_pages}/{len(pdf_reader.pages)}")
        
        extracted_text = text.strip()
        if not extracted_text:
            raise UserError(_("No text could be extracted from the PDF using pypdf."))
        
        _logger.info(f"Successfully extracted {len(extracted_text)} characters from PDF using pypdf")
        return extracted_text
    
    def _extract_with_pdfplumber(self, file_data):
        """Extract text using pdfplumber library"""
        pdf_file = io.BytesIO(file_data)
        
        try:
            with pdfplumber.open(pdf_file) as pdf:
                _logger.info(f"pdfplumber opened successfully. Number of pages: {len(pdf.pages)}")
                
                text = ''
                successful_pages = 0
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text += page_text + '\n'
                            successful_pages += 1
                            _logger.debug(f"Successfully extracted text from page {page_num + 1} with pdfplumber")
                    except Exception as page_error:
                        _logger.warning(f"Error extracting text from page {page_num + 1} with pdfplumber: {str(page_error)}")
                        continue
                
                _logger.info(f"pdfplumber extraction completed. Successful pages: {successful_pages}/{len(pdf.pages)}")
                
                extracted_text = text.strip()
                if not extracted_text:
                    raise UserError(_("No text could be extracted from the PDF using pdfplumber."))
                
                _logger.info(f"Successfully extracted {len(extracted_text)} characters from PDF using pdfplumber")
                return extracted_text
                
        except Exception as e:
            _logger.error(f"Error with pdfplumber: {str(e)}")
            raise
    
    def _extract_text_from_word(self, file_data):
        """Extract text from Word document"""
        if not docx:
            raise UserError(_("python-docx library is required for Word processing. Please install it."))
        
        try:
            doc_file = io.BytesIO(file_data)
            doc = docx.Document(doc_file)
            text = ''
            for paragraph in doc.paragraphs:
                text += paragraph.text + '\n'
            return text.strip()
        except Exception as e:
            _logger.error(f"Error extracting text from Word document: {str(e)}")
            raise UserError(_("Error reading Word document. Please ensure it's not corrupted."))
    
    def _extract_basic_info(self):
        """Extract basic candidate information from resume text"""
        if not self.resume_text:
            return
        
        text = self.resume_text.lower()
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, self.resume_text, re.IGNORECASE)
        if emails and not self.candidate_email:
            self.candidate_email = emails[0]
        
        # Extract phone
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{10,}'
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, self.resume_text)
            if phones and not self.candidate_phone:
                self.candidate_phone = phones[0]
                break
    
    def action_start_analysis(self):
        """Start the resume analysis process"""
        if not self.resume_file:
            raise UserError(_("Please upload a resume file first."))
        if not self.job_position_id:
            raise UserError(_("Please select a target job position."))
        
        self.state = 'analyzing'
        self.analysis_date = fields.Datetime.now()
        
        try:
            start_time = datetime.now()
            self._perform_analysis()
            end_time = datetime.now()
            self.analysis_duration = (end_time - start_time).total_seconds()
            self.state = 'completed'
            
            # Send notification
            self.message_post(
                body=_("Resume analysis completed successfully. Overall Score: %.1f%%") % self.overall_score,
                message_type='notification'
            )
            
        except Exception as e:
            _logger.error(f"Error during resume analysis: {str(e)}")
            self.state = 'failed'
            raise UserError(_("Analysis failed: %s") % str(e))
    
    def _perform_analysis(self):
        """Perform comprehensive resume analysis"""
        if not self.resume_text:
            self.resume_text = self._extract_text_from_file()
        
        # Perform different types of analysis
        self._analyze_ats_compatibility()
        self._analyze_skills_match()
        self._analyze_experience()
        self._analyze_education()
        self._analyze_keywords()
        
        # Calculate overall score
        self._calculate_overall_score()
        
        # Generate analysis summary
        self._generate_analysis_summary()
        
        # Generate recommendations
        self._generate_recommendations()
    
    def _analyze_ats_compatibility(self):
        """Analyze ATS compatibility of the resume"""
        score = 100.0
        issues = []
        
        # Check for common ATS issues
        text = self.resume_text.lower()
        
        # Penalize for complex formatting indicators
        if len(re.findall(r'[│┌┐└┘├┤┬┴┼]', self.resume_text)) > 5:
            score -= 15
            issues.append("Complex table formatting detected")
        
        # Check for standard sections
        required_sections = ['experience', 'education', 'skills']
        for section in required_sections:
            if section not in text:
                score -= 10
                issues.append(f"Missing {section} section")
        
        # Check for contact information
        if not self.candidate_email:
            score -= 10
            issues.append("Email address not found")
        
        if not self.candidate_phone:
            score -= 5
            issues.append("Phone number not found")
        
        # Bonus for good practices
        if any(keyword in text for keyword in ['summary', 'objective', 'profile']):
            score += 5
        
        self.ats_compatibility_score = max(0, min(100, score))
    
    def _analyze_skills_match(self):
        """Analyze how well candidate skills match job requirements"""
        if not self.job_position_id.required_skills:
            self.skills_match_score = 0
            return
        
        resume_text = self.resume_text.lower()
        required_skills = [skill.strip().lower() for skill in self.job_position_id.required_skills.split(',')]
        
        found_skills = []
        missing_skills = []
        
        for skill in required_skills:
            if skill in resume_text:
                found_skills.append(skill)
            else:
                missing_skills.append(skill)
        
        # Calculate score
        if required_skills:
            self.skills_match_score = (len(found_skills) / len(required_skills)) * 100
        else:
            self.skills_match_score = 0
        
        self.found_skills = ', '.join(found_skills)
        self.missing_skills = ', '.join(missing_skills)
        
        # Create skill analysis records
        self.skill_ids.unlink()
        for skill in required_skills:
            self.env['hr.resume.skill'].create({
                'resume_analysis_id': self.id,
                'skill_name': skill.title(),
                'is_found': skill in found_skills,
                'relevance_score': 100 if skill in found_skills else 0
            })
    
    def _analyze_experience(self):
        """Analyze candidate experience"""
        text = self.resume_text.lower()
        
        # Extract years of experience using various patterns
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'experience\s*:?\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*in\s*\w+'
        ]
        
        years_found = []
        for pattern in experience_patterns:
            matches = re.findall(pattern, text)
            years_found.extend([int(match) for match in matches])
        
        if years_found:
            self.total_experience_years = max(years_found)
        else:
            # Estimate based on job positions mentioned
            job_count = len(re.findall(r'\b(?:worked|employed|position|role)\b', text))
            self.total_experience_years = max(0, job_count * 1.5)  # Rough estimate
        
        # Calculate experience score based on job requirements
        required_experience = self.job_position_id.required_experience_years or 0
        if required_experience > 0:
            if self.total_experience_years >= required_experience:
                self.experience_score = 100
            else:
                self.experience_score = (self.total_experience_years / required_experience) * 100
        else:
            self.experience_score = 100 if self.total_experience_years > 0 else 50
        
        self.relevant_experience_years = self.total_experience_years * 0.8  # Assume 80% is relevant
    
    def _analyze_education(self):
        """Analyze candidate education"""
        text = self.resume_text.lower()
        
        # Education level detection
        education_keywords = {
            'phd': ['phd', 'ph.d', 'doctorate', 'doctoral'],
            'master': ['master', 'msc', 'm.sc', 'mba', 'm.b.a', 'ma', 'm.a'],
            'bachelor': ['bachelor', 'bsc', 'b.sc', 'ba', 'b.a', 'be', 'b.e', 'btech', 'b.tech'],
            'diploma': ['diploma', 'certificate'],
            'high_school': ['high school', 'secondary', 'matriculation']
        }
        
        detected_level = 'other'
        for level, keywords in education_keywords.items():
            if any(keyword in text for keyword in keywords):
                detected_level = level
                break
        
        self.education_level = detected_level
        
        # Calculate education score
        required_education = self.job_position_id.required_education_level
        education_hierarchy = ['high_school', 'diploma', 'bachelor', 'master', 'phd']
        
        if required_education and detected_level in education_hierarchy:
            required_index = education_hierarchy.index(required_education)
            candidate_index = education_hierarchy.index(detected_level)
            
            if candidate_index >= required_index:
                self.education_score = 100
            else:
                self.education_score = max(50, (candidate_index / required_index) * 100)
        else:
            self.education_score = 75  # Default score
    
    def _analyze_keywords(self):
        """Analyze keyword optimization"""
        if not self.job_position_id.keywords:
            self.keywords_score = 100
            return
        
        resume_text = self.resume_text.lower()
        keywords = [kw.strip().lower() for kw in self.job_position_id.keywords.split(',')]
        
        found_keywords = []
        missing_keywords = []
        
        for keyword in keywords:
            if keyword in resume_text:
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        if keywords:
            self.keywords_score = (len(found_keywords) / len(keywords)) * 100
        else:
            self.keywords_score = 100
        
        self.missing_keywords = ', '.join(missing_keywords)
    
    def _calculate_overall_score(self):
        """Calculate weighted overall score"""
        weights = {
            'ats_compatibility': 0.2,
            'skills_match': 0.3,
            'experience': 0.25,
            'education': 0.15,
            'keywords': 0.1
        }
        
        self.overall_score = (
            self.ats_compatibility_score * weights['ats_compatibility'] +
            self.skills_match_score * weights['skills_match'] +
            self.experience_score * weights['experience'] +
            self.education_score * weights['education'] +
            self.keywords_score * weights['keywords']
        )
    
    def _generate_analysis_summary(self):
        """Generate comprehensive analysis summary"""
        summary = f"""
        <div class="resume-analysis-summary">
            <h3>Resume Analysis Summary</h3>
            <div class="score-overview">
                <h4>Overall Score: {self.overall_score:.1f}%</h4>
                <div class="score-breakdown">
                    <p><strong>ATS Compatibility:</strong> {self.ats_compatibility_score:.1f}%</p>
                    <p><strong>Skills Match:</strong> {self.skills_match_score:.1f}%</p>
                    <p><strong>Experience:</strong> {self.experience_score:.1f}%</p>
                    <p><strong>Education:</strong> {self.education_score:.1f}%</p>
                    <p><strong>Keywords:</strong> {self.keywords_score:.1f}%</p>
                </div>
            </div>
            
            <div class="candidate-profile">
                <h4>Candidate Profile</h4>
                <p><strong>Total Experience:</strong> {self.total_experience_years:.1f} years</p>
                <p><strong>Education Level:</strong> {dict(self._fields['education_level'].selection).get(self.education_level, 'Not specified')}</p>
                <p><strong>Contact:</strong> {self.candidate_email or 'Not found'} | {self.candidate_phone or 'Not found'}</p>
            </div>
        </div>
        """
        self.analysis_summary = summary
    
    def _generate_recommendations(self):
        """Generate improvement recommendations"""
        recommendations = []
        strengths = []
        weaknesses = []
        
        # ATS Compatibility
        if self.ats_compatibility_score >= 80:
            strengths.append("Resume is well-formatted for ATS systems")
        else:
            weaknesses.append("Resume may have ATS compatibility issues")
            recommendations.append("Use standard section headings and avoid complex formatting")
        
        # Skills Match
        if self.skills_match_score >= 70:
            strengths.append(f"Good skills match ({self.skills_match_score:.1f}%)")
        else:
            weaknesses.append("Skills match could be improved")
            if self.missing_skills:
                recommendations.append(f"Consider highlighting these skills: {self.missing_skills}")
        
        # Experience
        if self.experience_score >= 80:
            strengths.append("Experience level meets job requirements")
        else:
            weaknesses.append("Experience level below job requirements")
            recommendations.append("Highlight relevant projects and achievements to demonstrate experience")
        
        # Education
        if self.education_score >= 80:
            strengths.append("Education level meets job requirements")
        else:
            weaknesses.append("Education level may not fully meet requirements")
            recommendations.append("Consider highlighting relevant certifications or training")
        
        # Keywords
        if self.keywords_score >= 70:
            strengths.append("Good keyword optimization")
        else:
            weaknesses.append("Keyword optimization needs improvement")
            if self.missing_keywords:
                recommendations.append(f"Include these important keywords: {self.missing_keywords}")
        
        self.strengths = '\n'.join([f"• {s}" for s in strengths])
        self.weaknesses = '\n'.join([f"• {w}" for w in weaknesses])
        self.recommendations = '\n'.join([f"• {r}" for r in recommendations])
    
    def action_reset_analysis(self):
        """Reset analysis to draft state"""
        self.write({
            'state': 'draft',
            'overall_score': 0,
            'ats_compatibility_score': 0,
            'skills_match_score': 0,
            'experience_score': 0,
            'education_score': 0,
            'keywords_score': 0,
            'analysis_summary': False,
            'strengths': False,
            'weaknesses': False,
            'recommendations': False,
            'analysis_date': False,
            'analysis_duration': 0,
        })
        self.skill_ids.unlink()
        self.experience_ids.unlink()
        self.education_ids.unlink()
    
    def action_view_report(self):
        """Open analysis report"""
        return {
            'type': 'ir.actions.report',
            'report_name': 'hr_resume_ats.resume_analysis_report_template',
            'report_type': 'qweb-pdf',
            'res_ids': [self.id],
            'context': self.env.context,
        }
