from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib import messages
from .models import BloodGroup, Donor, RequestBlood

def index(request):
    all_group = BloodGroup.objects.annotate(total=Count('donor'))
    return render(request, "index.html", {'all_group': all_group})


def donors_list(request, myid):
    blood_groups = BloodGroup.objects.filter(id=myid).first()
    donor = Donor.objects.filter(blood_group=blood_groups)
    return render(request, "donors_list.html", {'donor':donor})

def donors_details(request, myid):
    details = Donor.objects.filter(id=myid)[0]
    return render(request, "donors_details.html", {'details':details})

def request_blood(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        state = request.POST['state']
        city = request.POST['city']
        address = request.POST['address']
        blood_group = request.POST['blood_group']
        date = request.POST['date']
        try:
            blood_group_obj = BloodGroup.objects.get(name=blood_group)
            blood_request = RequestBlood.objects.create(
                name=name, email=email, phone=phone, state=state, city=city,
                address=address, blood_group=blood_group_obj, date=date)
            blood_request.save()
            return redirect('index')
        except BloodGroup.DoesNotExist:
            messages.error(request, "Blood group does not exist.")
    return render(request, "request_blood.html")

def see_all_request(request):
    requests = RequestBlood.objects.all()
    return render(request, "see_all_request.html", {'requests': requests})

def become_donor(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        state = request.POST['state']
        city = request.POST['city']
        address = request.POST['address']
        gender = request.POST['gender']
        blood_group = request.POST['blood_group']
        date = request.POST['date']
        image = request.FILES.get('image')
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('become_donor')

        username = email.split('@')[0]
        try:
            blood_group_obj = BloodGroup.objects.get(name=blood_group)
            user = User.objects.create_user(username=username, email=email, password=password,
                                            first_name=first_name, last_name=last_name)
            donor = Donor.objects.create(donor=user, phone=phone, state=state, city=city,
                                         address=address, gender=gender, blood_group=blood_group_obj,
                                         date_of_birth=date, image=image)
            user.save()
            donor.save()
            return redirect('index')
        except BloodGroup.DoesNotExist:
            messages.error(request, "Blood group does not exist.")
    return render(request, "become_donor.html")

def Login(request):
    if request.user.is_authenticated:
        return redirect('profile')
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.get(email=email)
            user = authenticate(username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
            else:
                messages.error(request, "Invalid email or password.")
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
    return render(request, "login.html")

def Logout(request):
    logout(request)
    return redirect('index')

@login_required(login_url='/login')
def profile(request):
    donor_profile = get_object_or_404(Donor, donor=request.user)
    return render(request, "profile.html", {'donor_profile': donor_profile})

@login_required(login_url='/login')
def edit_profile(request):
    donor_profile = get_object_or_404(Donor, donor=request.user)
    if request.method == "POST":
        donor_profile.donor.email = request.POST['email']
        donor_profile.phone = request.POST['phone']
        donor_profile.state = request.POST['state']
        donor_profile.city = request.POST['city']
        donor_profile.address = request.POST['address']

        try:
            image = request.FILES['image']
            donor_profile.image = image
        except KeyError:
            pass

        donor_profile.donor.save()
        donor_profile.save()

        messages.success(request, "Profile updated successfully.")
        return redirect('edit_profile')
    return render(request, "edit_profile.html", {'donor_profile': donor_profile})

@login_required(login_url='/login')
def change_status(request):
    donor_profile = get_object_or_404(Donor, donor=request.user)
    donor_profile.ready_to_donate = not donor_profile.ready_to_donate
    donor_profile.save()
    return redirect('profile')
