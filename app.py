from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lifelink.db'
app.secret_key = 'lifelink2026'
db = SQLAlchemy(app)

class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    blood_group = db.Column(db.String(10), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    available = db.Column(db.Boolean, default=True)
    approved = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    total_donors = Donor.query.filter_by(approved=True).count()
    cities = db.session.query(Donor.city).filter_by(approved=True).distinct().count()
    return render_template('index.html', total_donors=total_donors, cities=cities)

@app.route('/donor', methods=['GET', 'POST'])
def donor():
    success = False
    if request.method == 'POST':
        new_donor = Donor(
            name=request.form['name'],
            blood_group=request.form['blood_group'],
            city=request.form['city'],
            phone=request.form['phone'],
            available=True if request.form.get('available') == '1' else False,
            approved=False
        )
        db.session.add(new_donor)
        db.session.commit()
        success = True
    return render_template('donor.html', success=success)

@app.route('/donors')
def donors_list():
    all_donors = Donor.query.filter_by(approved=True).all()
    return render_template('Donors.html', donors=all_donors)

@app.route('/search')
def search():
    blood_group = request.args.get('blood_group')
    city = request.args.get('city')
    results = []
    if blood_group and city:
        results = Donor.query.filter_by(
            blood_group=blood_group,
            city=city,
            approved=True
        ).all()
    return render_template('search.html', results=results)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'javeriya' and password == 'jav@2026':
            session['admin'] = True
            return redirect('/admin/dashboard')
        else:
            error = 'Wrong username or password!'
    return render_template('admin_login.html', error=error)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect('/admin')
    pending = Donor.query.filter_by(approved=False).all()
    approved = Donor.query.filter_by(approved=True).all()
    return render_template('admin_dashboard.html', pending=pending, approved=approved)

@app.route('/admin/approve/<int:id>')
def approve_donor(id):
    if not session.get('admin'):
        return redirect('/admin')
    donor = Donor.query.get(id)
    donor.approved = True
    db.session.commit()
    return redirect('/admin/dashboard')

@app.route('/admin/delete/<int:id>')
def delete_donor(id):
    if not session.get('admin'):
        return redirect('/admin')
    donor = Donor.query.get(id)
    db.session.delete(donor)
    db.session.commit()
    return redirect('/admin/dashboard')

@app.route('/admin/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)