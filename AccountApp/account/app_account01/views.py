from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.db.models import Sum,Q
from django.db.models.functions import TruncMonth
from app_account01 import models
from app_account01.models import Account, User
from django.http import JsonResponse


class UserFormModel(forms.ModelForm):
    """用户注册数据库"""
    confirm_pwd = forms.CharField(label="Confirm Password",
                                  widget=forms.PasswordInput(attrs={'class': 'form-control',
        'placeholder': 'Confirm Password'}))
    class Meta:
        model = models.User
        fields = ['name', 'pwd', "confirm_pwd"]
        widgets = {
            'pwd' : forms.PasswordInput(attrs={'class': 'form-control',
                                                'placeholder': 'Password'}),
            'name' : forms.TextInput(attrs={'class': 'form-control','placeholder': 'Username'})
        }

    def clean_confirm_pwd(self):
        """钩子函数验证密码一致"""
        pwd = self.cleaned_data.get('pwd')
        cf_pwd = self.cleaned_data.get('confirm_pwd')
        if cf_pwd != pwd:
            raise ValidationError("Confirm Password does not match")
        return cf_pwd

class AccountFormModel(forms.ModelForm):
    """记账内容数据库"""
    class Meta:
        model = models.Account
        fields = ['expand', 'way','type','username','date']

def  enroll(request):
    """注册用户"""
    #弹出注册界面
    if request.method == "GET":
        form = UserFormModel()
        return render(request,"register.html",{"form":form})

    form = UserFormModel(data=request.POST)
    if form.is_valid():
        #校验是否为空
        form.save()
        #不为空，保存到数据库
        return redirect('/login/')

    return render(request,"register.html",{"form":form})

class LoginForm(forms.Form):
    name = forms.CharField(label="Name",
                           widget=forms.TextInput(attrs={'class':'form-control',
                                                         'placeholder': 'Username'},),
                           required =True)
    pwd = forms.CharField(label="Password",
                          widget=forms.PasswordInput(attrs={'class':'form-control',
                                                            'placeholder': 'Password'}),
                          required =True)

def login_user(request):
    """用户登录"""
    if request.method == "GET":
        form = LoginForm()
        return render(request,"denglu.html",{"form":form})

    #获取用户请求
    form = LoginForm(data=request.POST)
    if form.is_valid():
        admin_Login = models.User.objects.filter(**form.cleaned_data).first()
        if not admin_Login:
            # 用户名密码不正确
            form.add_error("name", "Wrong Username or Password")
            return render(request, "denglu.html", {"form": form})

        #用户名密码正确
        #生成随机找字符写进cookie，再储存进session
        request.session['info'] = form.cleaned_data['name']
        return redirect('/index/')


def forget(request):
    '''修改密码'''
    if request.method == "GET":
        return render(request,"forget-password.html")
    #获取姓名，跳转到重置密码界面
    name = request.POST.get("name")
    return redirect("/forget/{name}")

def forget_reset(request, name):
    """"重置密码"""
    row_data = models.User.objects.filter(name=name)
    if not row_data:
        return redirect("/login/")


def index(request):
    """记账界面"""

    #检查是否登录
    info = request.session.get('info')
    if not info:
        #没有登录则退回登录界面
        return redirect("/login/")

    #获取用户名,用户的记账记录
    username = info
    user = User.objects.get(name=username)
    records = Account.objects.filter(username=user)
    #分别计算入账和收账的总合和它们的差
    income_sum = Account.objects.filter(username=user, way= 2).aggregate(total=Sum('expand'))['total'] or 0
    expense_sum = Account.objects.filter(username=user, way= 1).aggregate(total=Sum('expand'))['total'] or 0
    balance = income_sum - expense_sum
    context = {
        "type_choice":models.Account.type_choice,
        "way_choice":models.Account.way_choice,
        "username": username,
        "records": records,
        "income_sum": income_sum,
        "expense_sum": expense_sum,
        "balance": balance,
    }

    #如果成功登录，跳转到记账界面
    if request.method == "GET":
        return render(request,"index.html",context)

    #获取用户的记账内容
    if request.method == "POST":
        amount = request.POST.get('expand')
        type = request.POST.get('type')
        way = request.POST.get('way')
        date = request.POST.get('date')
    #提交内容
    new_record = Account(expand=amount, way=way, type=type, username=user, date=date)
    new_record.save()
    return redirect("/index/")

def history(request):

    # 检查是否登录
    info = request.session.get('info')
    if not info:
        # 没有登录则退回登录界面
        return redirect("/login/")

    # 获取用户名,用户的记账记录
    username = info
    user = User.objects.get(name=username)
    records = Account.objects.filter(username=user)

    form = AccountFormModel()
    context = {
        "records": records,
        "form": form,
    }
    if request.method == "GET":
        return render(request,"history.html",context)

def chart(request):
    #图表页面
    return render(request,"chart.html")
def chart_type(request):
    """传回每个月所花费的类型数据"""
    # 检查是否登录
    info = request.session.get('info')
    if not info:
        # 没有登录则退回登录界面
        return redirect("/login/")

    date = request.GET.get('month')  # 获取前端传递的月份
    if date:
        #把传入的日期的年月分开
        year, month = map(int, date.split('-'))

    #获取指定用户的信息并把从信息中提取指定的月份，按钱款流向和分类划分加和
    username = info
    user = User.objects.get(name=username)
    records = Account.objects.filter(username=user,date__month=month)
    category_totals = records.values('type', 'way').annotate(total_spent=Sum('expand')).order_by('type')

    categories = []
    expense_totals = []
    income_totals = []
    x_axis = []
    for category in category_totals:
        category_label = Account._meta.get_field('type').choices[category['type'] - 1][1]

        if category['way'] == 2:# 收入
            if category_label not in categories:
                x_axis.append(category_label)
                categories.append(category_label)
            income_totals.append(category['total_spent'])

        elif category['way'] == 1:  # 支出
            if category_label not in x_axis and category_label != '饮食':
                categories.append(category_label)
                x_axis.append(category_label)
                income_totals.append(0)
            expense_totals.append(category['total_spent'])

    legend = ['花销','收入']

    series_list = [{
                'name': '花销',
                'type': 'bar',
                'data': expense_totals
     },{
        'name': '收入',
        'type': 'bar',
        'data': income_totals
    }]

    result = {
        'status': True,
        'data':{'x_axis': x_axis,
        'series_list': series_list,
        'legend_': legend,}
    }

    return JsonResponse(result)

def chart_month(request):
    """提取每个月的收入支出总数"""
    info = request.session.get('info')
    if not info:
        # 没有登录则退回登录界面
        return redirect("/login/")

    # 获取用户名,用户的记账记录
    username = info
    user = User.objects.get(name=username)
    records = Account.objects.filter(username=user).annotate(month=TruncMonth('date'))
    monthly_totals = records.values('month') \
        .annotate(total_expense=Sum('expand'), total_spent=Sum('expand', filter=Q(way=1)),
                  total_income=Sum('expand', filter=Q(way=2))) \
        .order_by('month')

    # 准备数据传回前端
    months = []
    expense_totals = []
    income_totals = []

    for month_data in monthly_totals:
        months.append(month_data['month'].strftime('%Y-%m'))
        expense_totals.append(month_data['total_spent'] or 0)
        income_totals.append(month_data['total_income'] or 0)
    series_list = [{
                    'name': '花销',
                    'type': 'bar',
                    'data': expense_totals
         },{
            'name': '收入',
            'type': 'bar',
            'data': income_totals
        }]

    result = {
            'status': True,
            'data':{'x_axis': months,
            'series_list': series_list,
            'legend_': ['花销','收入'],}
        }
    return JsonResponse(result)