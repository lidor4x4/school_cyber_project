data = "SIGN_UP, DrSaveMe@gmail.com, 123123123, Lior Narkis, patient"
fields = data.split(', ')[1:]  # Remove the 'SIGN_UP,' part and keep the rest
email, password, username, user_type = map(str.strip, fields)  # Strip any surrounding spaces
print(email)
print(password)
print(username)
print(user_type)