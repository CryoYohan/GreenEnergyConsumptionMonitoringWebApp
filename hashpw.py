import bcrypt
class PasswordHashing:
    
    def hashpassword(self,plain_password):
        plain_password_bytes = plain_password.encode('utf-8') # Convert plain text to bytes
        hashed_password = bcrypt.hashpw(plain_password_bytes,bcrypt.gensalt()) # Generate salt and hash the password
        return hashed_password.decode('utf-8')
    
    def check_password(self,plain_password, hashed_password):
        plain_password_bytes = plain_password.encode('utf-8')
        hashed_password_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_password_bytes,hashed_password_bytes)
    

