from app import app, db, User

app.app_context().push()
user = User.query.filter_by(username='vitor').first()
if user:
    user.set_password('Brasmid@2023')
    db.session.commit()
    print('Senha redefinida com sucesso para o usuário vitor')
else:
    print('Usuário não encontrado')
