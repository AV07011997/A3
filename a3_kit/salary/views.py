from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Salary
from common.scripts import previous_months_list


@login_required
def upload_salary_page(request):
    status = {}
    if "deal_id" not in request.session or "customer_id" not in request.session:
        status["type"] = "deal"
        status["message"] = "Please select a deal first!"
    else:
        customer_id = request.session["customer_id"]
        deal_id=request.session["deal_id"]
    
    if not status and request.method == "POST":
        if 'stype' not in request.POST or 'month1' not in request.POST or 'month2' not in request.POST or 'month3' not in request.POST or 'month4' not in request.POST or 'month5' not in request.POST or 'month6' not in request.POST:
            status["type"] = "other"
            status["message"] = "Field name is missing, can not procceed further!"
        
        if not status:
            status["type"] = "success"
            status["message"] = "Salary updation successful!"
            
            if status["type"] == "success":
                try:
                    db_check = Salary.objects.get(deal_id=deal_id,customer_id=customer_id,sal_type=request.POST["stype"])
                except Exception as e:
                    print(e)
                    db_check = None

                try:
                    if db_check:
                        db_check.month1 = request.POST["month1"]
                        db_check.month2 = request.POST["month2"]
                        db_check.month3 = request.POST["month3"]
                        db_check.month4 = request.POST["month4"]
                        db_check.month5 = request.POST["month5"]
                        db_check.month6 = request.POST["month6"]
                        db_check.month7 = request.POST["month7"]
                        db_check.save()
                    else:
                        Salary.objects.create(sal_type=request.POST["stype"],
                                            month1=request.POST["month1"],
                                            month2=request.POST["month2"],
                                            month3=request.POST["month3"],
                                            month4=request.POST["month4"],
                                            month5=request.POST["month5"],
                                            month6=request.POST["month6"],
                                            month7=request.POST["month7"],
                                            deal_id=request.session["deal_id"],
                                            customer_id=request.session["customer_id"],
                                            created_by=request.user)
                except Exception as e:
                    print(e)
                    status["type"] = "other"
                    status["message"] = "Something went wrong! please try again!"
    
    if status and status["type"] != "deal":
        return JsonResponse({"status": status})
    try:
        net_salary_db_data = Salary.objects.get(deal_id=deal_id,customer_id=customer_id,sal_type="net")
        net_salary_data = {"sal_type": net_salary_db_data.sal_type if net_salary_db_data.sal_type else "-", "month1": net_salary_db_data.month1 if net_salary_db_data.month1 else "-", "month2": net_salary_db_data.month2 if net_salary_db_data.month2 else "-", "month3": net_salary_db_data.month3 if net_salary_db_data.month3 else "-", "month4": net_salary_db_data.month4 if net_salary_db_data.month4 else "-", "month5": net_salary_db_data.month5 if net_salary_db_data.month5 else "-", "month6": net_salary_db_data.month6 if net_salary_db_data.month6 else "-", "month7": net_salary_db_data.month7 if net_salary_db_data.month7 else "-"}
    except:
        net_salary_data = {"sal_type": "-", "month1": "-", "month2": "-", "month3": "-", "month4": "-", "month5": "-", "month6": "-", "month7": "-"}
    
    try:
        gross_salary_db_data = Salary.objects.get(deal_id=deal_id,customer_id=customer_id,sal_type="gross")
        gross_salary_data = {"sal_type": gross_salary_db_data.sal_type if gross_salary_db_data.sal_type else "-", "month1": gross_salary_db_data.month1 if gross_salary_db_data.month1 else "-", "month2": gross_salary_db_data.month2 if gross_salary_db_data.month2 else "-", "month3": gross_salary_db_data.month3 if gross_salary_db_data.month3 else "-", "month4": gross_salary_db_data.month4 if gross_salary_db_data.month4 else "-", "month5": gross_salary_db_data.month5 if gross_salary_db_data.month5 else "-", "month6": gross_salary_db_data.month6 if gross_salary_db_data.month6 else "-", "month7": gross_salary_db_data.month7 if gross_salary_db_data.month7 else "-"}
    except:
        gross_salary_data = {"sal_type": "-", "month1": "-", "month2": "-", "month3": "-", "month4": "-", "month5": "-", "month6": "-", "month7": "-"}

    payload = {"salary_page": True, "previous_months_list": previous_months_list(7), "upload_salary_page": True, "net_salary_data": net_salary_data, "gross_salary_data": gross_salary_data, "status": status if status else None}
    return render(request, "upload_salary.html", payload)
