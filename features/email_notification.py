import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContractNotificationManager:
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587):
        """Initialize the email notification manager with SMTP settings."""
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = os.environ.get('NOTIFICATION_EMAIL', '')
        self.sender_password = os.environ.get('NOTIFICATION_PASSWORD', '')
        # Days before expiration to send notifications
        self.notification_days = [1, 3, 5]
        
        # Store pending notifications
        self.notifications_file = "contract_notifications.json"
        self.notifications = self._load_notifications()
    
    def _load_notifications(self):
        """Load existing notifications from file."""
        try:
            if os.path.exists(self.notifications_file):
                with open(self.notifications_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading notifications: {e}")
            return {}
    
    def _save_notifications(self):
        """Save notifications to file."""
        try:
            with open(self.notifications_file, 'w') as f:
                json.dump(self.notifications, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving notifications: {e}")
    
    def schedule_notifications(self, contract_data, recipient_email, contract_id=None):
        """
        Schedule notifications for a contract termination date.
        
        Args:
            contract_data: Dictionary containing contract details
            recipient_email: Email address to send notifications to
            contract_id: Unique identifier for the contract (optional)
        """
        try:
            # Extract termination date from contract data
            term_duration = contract_data.get("licensing_terms", {}).get("term_duration", "")
            effective_date_str = contract_data.get("licensing_terms", {}).get("effective_date", "")
            
            # Skip if we don't have the necessary information
            if not effective_date_str:
                logger.warning("No effective date found in contract data")
                return False
            
            # Generate contract ID if not provided
            if not contract_id:
                contract_id = f"contract_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Parse effective date
            effective_date = self._parse_date(effective_date_str)
            if not effective_date:
                logger.warning(f"Could not parse effective date: {effective_date_str}")
                return False
            
            # Calculate termination date based on term duration
            termination_date = self._calculate_termination_date(effective_date, term_duration)
            if not termination_date:
                logger.warning(f"Could not calculate termination date from {term_duration}")
                return False
            
            # Create notification schedule
            today = datetime.now().date()
            notifications = []
            
            for days in self.notification_days:
                notification_date = termination_date - timedelta(days=days)
                # Only schedule future notifications
                # if notification_date >= today:
                notifications.append({
                    "days_before": days,
                    "notification_date": notification_date.strftime("%Y-%m-%d"),
                    "sent": False
                })
            
            # Store notification schedule
            self.notifications[contract_id] = {
                "recipient_email": recipient_email,
                "contract_name": f"{contract_data.get('parties', {}).get('licensor', 'Unknown')} - {contract_data.get('parties', {}).get('licensee', 'Unknown')}",
                "termination_date": termination_date.strftime("%Y-%m-%d"),
                "notifications": notifications
            }
            
            self._save_notifications()
            logger.info(f"Scheduled notifications for contract {contract_id} terminating on {termination_date}")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling notifications: {e}")
            return False
    
    def _parse_date(self, date_str):
        """
        Parse date string into datetime object.
        Tries multiple formats to be flexible.
        """
        date_formats = [
            "%Y-%m-%d", 
            "%m/%d/%Y", 
            "%d/%m/%Y", 
            "%B %d, %Y", 
            "%d %B %Y"
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        return None
    
    def _calculate_termination_date(self, effective_date, term_duration):
        """
        Calculate termination date based on effective date and term duration.
        
        Args:
            effective_date: Start date of the contract
            term_duration: String describing the duration (e.g., "12 months", "1 year")
        
        Returns:
            datetime.date object representing termination date
        """
        try:
            term_lower = term_duration.lower()
            
            # Check for years
            if "year" in term_lower:
                years = int(term_lower.split()[0])
                return datetime(effective_date.year + years, effective_date.month, effective_date.day).date()
            
            # Check for months
            elif "month" in term_lower:
                months = int(term_lower.split()[0])
                new_month = effective_date.month + months
                years_to_add = (new_month - 1) // 12
                final_month = ((new_month - 1) % 12) + 1
                return datetime(effective_date.year + years_to_add, final_month, effective_date.day).date()
            
            # Check for days
            elif "day" in term_lower:
                days = int(term_lower.split()[0])
                return effective_date + timedelta(days=days)
            
            # If exact date is specified
            elif "until" in term_lower:
                date_part = term_lower.split("until", 1)[1].strip()
                return self._parse_date(date_part)
            
            else:
                logger.warning(f"Unrecognized term duration format: {term_duration}")
                return None
                
        except Exception as e:
            logger.error(f"Error calculating termination date: {e}")
            return None
    
    def send_scheduled_notifications(self):
        """Check and send all due or past due notifications."""
        today = datetime.now().date().strftime("%Y-%m-%d")
        notifications_modified = False

        for contract_id, contract_info in self.notifications.items():
            for notification in contract_info["notifications"]:
                # Check if notification date is today OR in the past AND not sent.
                if notification["notification_date"] == today and not notification["sent"]:
                    # Send notification
                    success = self._send_notification_email(
                        contract_info["recipient_email"],
                        contract_info["contract_name"],
                        contract_info["termination_date"],
                        notification["days_before"]
                    )

                    if success:
                        notification["sent"] = True
                        notifications_modified = True
                        logger.info(f"Sent notification for contract {contract_id} - {notification['days_before']} days before termination")

        if notifications_modified:
            self._save_notifications()    

    def _send_notification_email(self, recipient_email, contract_name, termination_date, days_before):
        """
        Send notification email.
        
        Args:
            recipient_email: Email address to send to
            contract_name: Name of the contract (for subject line)
            termination_date: Contract termination date (string)
            days_before: Days before termination
        
        Returns:
            Boolean indicating success/failure
        """
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"Contract Termination Notice: {contract_name} - {days_before} day{'s' if days_before > 1 else ''} remaining"
            
            # Create email body
            body = f"""
            <html>
            <body>
                <h2>Contract Termination Reminder</h2>
                <p>This is a reminder that the following contract is set to terminate in <strong>{days_before} day{'s' if days_before > 1 else ''}</strong>:</p>
                
                <div style="margin: 20px; padding: 15px; border: 1px solid #ccc; border-radius: 5px;">
                    <p><strong>Contract:</strong> {contract_name}</p>
                    <p><strong>Termination Date:</strong> {termination_date}</p>
                </div>
                
                <p>Please take any necessary actions before the contract expires.</p>
                
                <p>This is an automated notification from ContractIQ.</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Connect to SMTP server and send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending notification email: {e}")
            return False
if __name__ == '__main__':
    obj = ContractNotificationManager()
    obj.send_scheduled_notifications()
