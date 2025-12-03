data = f"SIGN_UP, {'email'}, {'password'}, {'username'}"

# Extract the part after 'SIGN_UP, ' and split by commas
fields = data.split(', ')[1:]  # This removes the 'SIGN_UP,' part and keeps the rest

# Assign each field to its own variable
email = fields[0].strip()    # Strip any surrounding spaces
password = fields[1].strip()
username = fields[2].strip()

# Print each variable on its own line
print(f"e = {email}")
print(f"p = {password}")
print(f"u = {username}")
