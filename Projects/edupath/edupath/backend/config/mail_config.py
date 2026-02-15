from flask_mail import Mail, Message
from flask import current_app
import os
import random
import string
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

mail = Mail()

# In-memory OTP storage (use Redis in production)
otp_storage = {}

def init_mail(app):
    """Initialize Flask-Mail with better error handling"""
    # Mail server configuration
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))
    
    # Debug settings
    app.config['MAIL_DEBUG'] = True
    app.config['MAIL_SUPPRESS_SEND'] = False
    
    print(f"📧 Mail Configuration:")
    print(f"  Server: {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']}")
    print(f"  TLS: {app.config['MAIL_USE_TLS']}")
    print(f"  SSL: {app.config['MAIL_USE_SSL']}")
    print(f"  Username: {app.config['MAIL_USERNAME']}")
    print(f"  Password: {'*' * len(app.config['MAIL_PASSWORD']) if app.config['MAIL_PASSWORD'] else 'NOT SET'}")
    
    mail.init_app(app)
    return mail

def generate_otp():
    """Generate 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email_direct(email: str, otp: str):
    """
    Send OTP via direct SMTP (fallback method)
    More reliable than Flask-Mail for Gmail
    """
    try:
        smtp_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('MAIL_PORT', 587))
        smtp_username = os.getenv('MAIL_USERNAME')
        smtp_password = os.getenv('MAIL_PASSWORD')
        
        if not smtp_username or not smtp_password:
            print("❌ MAIL_USERNAME or MAIL_PASSWORD not set in .env")
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'EduPath - Verify Your Email'
        msg['From'] = f"EduPath <{smtp_username}>"
        msg['To'] = email
        
        # HTML content
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #0e3248 0%, #2f4954 100%); padding: 30px; border-radius: 12px 12px 0 0;">
                <h1 style="color: #f5cb7d; margin: 0; font-size: 28px;">📚 EduPath</h1>
            </div>
            
            <div style="background: white; padding: 40px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="color: #1f3e4e; margin-top: 0;">Verify Your Email Address</h2>
                
                <p style="color: #636e65; font-size: 16px; line-height: 1.6;">
                    Thank you for signing up! Please use the following OTP to verify your email address:
                </p>
                
                <div style="background: #f8f9fa; border-left: 4px solid #f5cb7d; padding: 20px; margin: 30px 0; border-radius: 8px;">
                    <p style="margin: 0; color: #636e65; font-size: 14px; font-weight: 600;">YOUR OTP CODE</p>
                    <p style="margin: 10px 0 0 0; font-size: 36px; font-weight: bold; color: #1f3e4e; letter-spacing: 8px;">
                        {otp}
                    </p>
                </div>
                
                <p style="color: #636e65; font-size: 14px;">
                    <strong>This OTP will expire in 10 minutes.</strong>
                </p>
                
                <p style="color: #8a9189; font-size: 13px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                    If you didn't request this, please ignore this email.
                </p>
            </div>
            
            <div style="text-align: center; margin-top: 20px; color: #8a9189; font-size: 12px;">
                <p>© 2026 EduPath - Your Learning Companion</p>
            </div>
        </div>
        """
        
        # Plain text fallback
        text = f"""
        EduPath - Email Verification
        
        Your OTP code is: {otp}
        
        This code will expire in 10 minutes.
        
        If you didn't request this, please ignore this email.
        """
        
        # Attach parts
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send via SMTP
        print(f"📧 Connecting to {smtp_server}:{smtp_port}...")
        
        # Try with TLS
        try:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
            server.set_debuglevel(1)  # Enable debug output
            server.ehlo()
            
            if server.has_extn('STARTTLS'):
                print("🔒 Starting TLS...")
                server.starttls()
                server.ehlo()
            
            print(f"🔑 Logging in as {smtp_username}...")
            server.login(smtp_username, smtp_password)
            
            print(f"📤 Sending email to {email}...")
            server.sendmail(smtp_username, email, msg.as_string())
            server.quit()
            
            print(f"✅ OTP email sent successfully to {email}")
            return True
            
        except Exception as e:
            print(f"❌ SMTP Error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to send OTP email: {e}")
        import traceback
        traceback.print_exc()
        return False

def send_otp_email(email: str, otp: str):
    """Send OTP via email - tries Flask-Mail first, then direct SMTP"""
    
    # Try Flask-Mail first
    try:
        msg = Message(
            subject='EduPath - Verify Your Email',
            recipients=[email],
            html=f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #0e3248 0%, #2f4954 100%); padding: 30px; border-radius: 12px 12px 0 0;">
                    <h1 style="color: #f5cb7d; margin: 0; font-size: 28px;">📚 EduPath</h1>
                </div>
                
                <div style="background: white; padding: 40px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h2 style="color: #1f3e4e; margin-top: 0;">Verify Your Email Address</h2>
                    
                    <p style="color: #636e65; font-size: 16px; line-height: 1.6;">
                        Thank you for signing up! Please use the following OTP to verify your email address:
                    </p>
                    
                    <div style="background: #f8f9fa; border-left: 4px solid #f5cb7d; padding: 20px; margin: 30px 0; border-radius: 8px;">
                        <p style="margin: 0; color: #636e65; font-size: 14px; font-weight: 600;">YOUR OTP CODE</p>
                        <p style="margin: 10px 0 0 0; font-size: 36px; font-weight: bold; color: #1f3e4e; letter-spacing: 8px;">
                            {otp}
                        </p>
                    </div>
                    
                    <p style="color: #636e65; font-size: 14px;">
                        <strong>This OTP will expire in 10 minutes.</strong>
                    </p>
                    
                    <p style="color: #8a9189; font-size: 13px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                        If you didn't request this, please ignore this email.
                    </p>
                </div>
                
                <div style="text-align: center; margin-top: 20px; color: #8a9189; font-size: 12px;">
                    <p>© 2026 EduPath - Your Learning Companion</p>
                </div>
            </div>
            """
        )
        
        mail.send(msg)
        print(f"✅ OTP email sent to {email} via Flask-Mail")
        return True
        
    except Exception as e:
        print(f"⚠️ Flask-Mail failed: {e}")
        print(f"🔄 Trying direct SMTP...")
        
        # Fallback to direct SMTP
        return send_otp_email_direct(email, otp)

def store_otp(email: str, otp: str):
    """Store OTP with expiry (10 minutes)"""
    expiry = datetime.now() + timedelta(minutes=10)
    otp_storage[email] = {
        'otp': otp,
        'expiry': expiry,
        'attempts': 0
    }
    print(f"🔐 OTP stored for {email}, expires at {expiry}")

def verify_otp(email: str, otp: str) -> dict:
    """Verify OTP"""
    if email not in otp_storage:
        return {'valid': False, 'error': 'No OTP found. Please request a new one.'}
    
    stored = otp_storage[email]
    
    # Check expiry
    if datetime.now() > stored['expiry']:
        del otp_storage[email]
        return {'valid': False, 'error': 'OTP expired. Please request a new one.'}
    
    # Check attempts
    if stored['attempts'] >= 5:
        del otp_storage[email]
        return {'valid': False, 'error': 'Too many attempts. Please request a new OTP.'}
    
    # Verify OTP
    if stored['otp'] == otp:
        del otp_storage[email]
        return {'valid': True}
    else:
        stored['attempts'] += 1
        return {'valid': False, 'error': f'Invalid OTP. {5 - stored["attempts"]} attempts remaining.'}