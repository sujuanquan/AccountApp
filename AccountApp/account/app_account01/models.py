from django.db import models

class User(models.Model):
    '''用户信息'''
    name = models.CharField(verbose_name="Username",max_length=120)
    pwd = models.CharField(verbose_name="Password", max_length=120)


    def __str__(self):
        return self.name

class Account(models.Model):
    '''记账信息'''
    #入出账金额
    expand = models.IntegerField(verbose_name="Expand",default= 0)

    #金钱流向
    way_choice = (
        (1, "支出"),
        (2, "收入")
    )
    way = models.IntegerField(verbose_name="way", choices=way_choice, default=1)

    #消费种类
    type_choice = (
        (1, "饮食"),
        (2, "购物"),
        (3, "出行"),
        (4, "教育"),
        (5, "娱乐"),
        (6, "人情"),
        (7, "居住"),
        (8, "医疗"),
        (9, "投资"),
        (10, "其他"),
    )
    type = models.IntegerField(verbose_name="Type", choices=type_choice, default=1)

    #用户名
    username = models.ForeignKey(User,verbose_name="Username",on_delete=models.CASCADE,default=None)

    #消费日期
    date = models.DateField(verbose_name="Date",default=None)
