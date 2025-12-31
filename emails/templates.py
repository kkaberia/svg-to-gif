def welcome_email_template(username, password):
    return f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f9f9f9;
                }}
                .container {{
                    max-width: 600px;
                    margin: 20px auto;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    background-color: #fff;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }}
                h1 {{
                    color: #2c3e50;
                    font-size: 24px;
                    margin-bottom: 20px;
                    text-align: center;
                }}
                p {{
                    margin: 10px 0;
                    font-size: 16px;
                }}
                .details {{
                    background-color: #f5f5f5;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
                .details p {{
                    margin: 5px 0;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 14px;
                    color: #777;
                    text-align: center;
                }}
                .button {{
                    display: inline-block;
                    margin: 20px 0;
                    padding: 12px 24px;
                    background-color: #3498db;
                    color: #fff;
                    text-decoration: none;
                    border-radius: 5px;
                    font-size: 16px;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Welcome to Plateau Estate Portal</h1>
                <p>Hello {username},</p>
                <p>Your account has been created successfully. Here are your login details:</p>
                
                <div class="details">
                    <p><strong>Username:</strong> {username}</p>
                    <p><strong>Password:</strong> {password}</p>
                </div>

                <p>Please log in and change your password as soon as possible.</p>
                <a href="https://your-portal-url.com/login" class="button">Log In Now</a>

                <div class="footer">
                    <p>Best regards,</p>
                    <p><strong>Plateau Estate Portal Team</strong></p>
                </div>
            </div>
        </body>
    </html>
    """


def payment_confirmation_email_template(user, amount, payment_type, payment_date, months_str, origin_bank):
    return f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    background-color: #f9f9f9;
                }}
                h1 {{
                    color: #2c3e50;
                    font-size: 24px;
                    margin-bottom: 20px;
                }}
                .details {{
                    margin-bottom: 20px;
                }}
                .details p {{
                    margin: 5px 0;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 14px;
                    color: #777;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Hello {user.first_name},</h1>
                <div class="details">
                    <p>A new payment has been received in the bank, and we have updated the members payment register:</p>
                    <p><strong>Amount:</strong> {amount}</p>
                    <p><strong>Payment Type:</strong> {payment_type}</p>
                    <p><strong>Payment Date:</strong> {payment_date}</p>
                    <p><strong>Months:</strong> {months_str if months_str else "N/A"}</p>
                    <p><strong>Originating Bank:</strong> {origin_bank if origin_bank else "N/A"}</p>
                </div>
                <p>Thank you for the payment and for making our Cluster better!</p>
                <div class="footer">
                    <p>Best regards,</p>
                    <p><strong>Treasurer,</strong></p>
                    <p><strong>Plateau Cluster</strong></p>
                </div>
            </div>
        </body>
    </html>
    """


def password_reset_email_template(username, reset_url):
    return f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f9f9f9;
                }}
                .container {{
                    max-width: 600px;
                    margin: 20px auto;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    background-color: #fff;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }}
                h1 {{
                    color: #2c3e50;
                    font-size: 24px;
                    margin-bottom: 20px;
                    text-align: center;
                }}
                p {{
                    margin: 10px 0;
                    font-size: 16px;
                }}
                .button {{
                    display: inline-block;
                    margin: 20px 0;
                    padding: 12px 24px;
                    background-color: #3498db;
                    color: #fff;
                    text-decoration: none;
                    border-radius: 5px;
                    font-size: 16px;
                    text-align: center;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 14px;
                    color: #777;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Password Reset Request</h1>
                <p>Hello {username},</p>
                <p>We received a request to reset your password. Click the button below to reset it:</p>
                <a href="{reset_url}" class="button">Reset Password</a>
                <p>If you didn't request this, please ignore this email. Your password will remain unchanged.</p>
                <div class="footer">
                    <p>Best regards,</p>
                    <p><strong>Plateau Cluster System Admin</strong></p>
                </div>
            </div>
        </body>
    </html>
    """