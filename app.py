from flask import Flask ,request,render_template
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import pickle
from datetime import datetime  # Import datetime
import shap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO
app = Flask(__name__)
# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///submissions.db'
db = SQLAlchemy(app)

# load model
model=pickle.load(open('model.pkl','rb'))
# Database model for storing prediction form data
class PredictionFormData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(10))
    married = db.Column(db.String(10))
    dependents = db.Column(db.String(10))
    education = db.Column(db.String(20))
    employed = db.Column(db.String(10))
    credit = db.Column(db.Float)
    area = db.Column(db.String(20))
    applicant_income = db.Column(db.Float)
    coapplicant_income = db.Column(db.Float)
    loan_amount = db.Column(db.Float)
    loan_term = db.Column(db.Float)
    prediction_result = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Corrected line


@app.route("/")
def index():
    return render_template("index.html")
@app.route('/about')
def about():
    return render_template('aboutus.html')

@app.route("/prediction" , methods=['GET','POST'])
def predict():
    if request.method =='POST':
        gender = request.form['gender']
        married = request.form['married']
        dependents = request.form['dependents']
        education = request.form['education']
        employed = request.form['employed']
        credit = float(request.form.get('credit',0))
        area = request.form['area']
        ApplicantIncome = float(request.form.get('applicantIncome', 0))  
        CoapplicantIncome = float(request.form.get('coapplicantIncome', 0)) 
        LoanAmount = float(request.form.get('loanAmount', 0))  
        Loan_Amount_Term = float(request.form.get('loanAmountTerm',0))
        

        gender_val = 1 if gender == "Male" else 0
        married_val = 1 if married == "Yes" else 0
        dependents_val = 3 if dependents == "3+" else int(dependents)
        education_val = 1 if education == "Graduate" else 0
        employed_val = 1 if employed == "Yes" else 0
        area_dict = {"Rural": 0, "Semiurban": 1, "Urban": 2}
        area_val = area_dict.get(area, 0)

        ApplicantIncomelog = np.log(ApplicantIncome + 1e-10) 
        CoapplicantIncomelog = np.log(CoapplicantIncome + 1e-10) 
        Totalincomelog = np.log(ApplicantIncome+CoapplicantIncome + 1e-10) 
        LoanAmountlog = np.log(LoanAmount + 1e-10)
        Loan_Amount_Termlog = np.log(Loan_Amount_Term + 1e-10) 

        # Combine all inputs as expected by model and make prediction
        input_features =np.array ([[ gender_val, married_val,dependents_val,
                              education_val, employed_val,credit,
                              area_val,ApplicantIncomelog, CoapplicantIncomelog,
                              LoanAmountlog,   Loan_Amount_Termlog , Totalincomelog]])

        now=datetime.utcnow()

        # Render result to a web page
        prediction = model.predict(input_features)

        result_text = "Approved" if prediction[0] == 1 else "Rejected"
        
       # Save submission to DB
        entry = PredictionFormData(
            gender=gender,
            married=married,
            dependents=dependents,
            education=education,
            employed=employed,
            credit=credit,
            area=area,
            applicant_income=ApplicantIncome,
            coapplicant_income=CoapplicantIncome,
            loan_amount=LoanAmount,
            loan_term=Loan_Amount_Term,
            prediction_result=result_text,
            timestamp=now
        )
        db.session.add(entry)
        db.session.commit()
        print("Entry saved to database")  # Keep this for logging
        return render_template('prediction.html', prediction_text=f'Loan Status: {result_text}')
    return render_template("prediction.html")
# Admin route to view all submissions
@app.route("/admin")
def admin():
    entries = PredictionFormData.query.all()
    return render_template("admin.html", entries=entries)

@app.route('/suggestion', methods=['GET', 'POST'])
def suggestion():
    if request.method == 'POST':
        married = request.form['married']
        education = request.form['education']
        employed = request.form['employed']
        area = request.form['area']
        try:
            total_income = float(request.form.get('TotalIncome', 0))
        except ValueError:
            total_income = 0  # Handle invalid input

        if total_income > 5000:
            loan_type = "Home Loan"
        elif education == 'Graduate':
            loan_type = "Education Loan"
        elif area == 'Urban':
            loan_type = "Personal Loan"
        elif married == 'Yes' and 3000 < total_income <= 5000:
            loan_type = "Marriage Loan"
        else:
            loan_type = "Agricultural Loan"

        
        # Render result to a web page with the loan type from the model prediction
        return render_template('suggestion.html', suggestion_text=f'Suggestion For Loan Type is: {loan_type}')

    return render_template('suggestion.html')
 
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
       