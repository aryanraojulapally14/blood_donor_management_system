
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Donor, Hospital, BloodRequest
import math
from .forms import DonorRegisterForm, HospitalRegisterForm, LoginForm
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login
import threading
import time
from django.shortcuts import get_object_or_404





def home(request):
    return render(request,'home.html')



def register_donor(request):
    form = DonorRegisterForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():

        username = form.cleaned_data['username']

        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Try another.")
            return render(request, 'register_donor.html', {'form': form})

        # Create User
        user = User.objects.create_user(
            username=username,
            password=form.cleaned_data['password'],
            email=form.cleaned_data['email']
        )

        # Create Donor
        donor = form.save(commit=False)
        donor.user = user
        donor.save()

        #  Auto login
        login(request, user)

        messages.success(request, "Registration successful!")

        return redirect('dashboard')

    return render(request, 'register_donor.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')


def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )

        if user:
            login(request, user)
            return redirect('dashboard')

    return render(request, 'login.html', {'form': form})



def dashboard(request):
    donor = None
    days_left = None
    requests = None

    #  Check if logged-in user is a donor
    if Donor.objects.filter(user=request.user).exists():
        donor = Donor.objects.get(user=request.user)

        #  Calculate eligibility (90 days rule)
        if donor.last_donation_date:
            next_date = donor.last_donation_date + timedelta(days=90)
            today = timezone.now().date()

            if today < next_date:
                days_left = (next_date - today).days

        #  Get all blood requests (latest first)
        requests = BloodRequest.objects.all().order_by('-id')

    return render(request, 'dashboard.html', {
        'donor': donor,
        'days_left': days_left,
        'requests': requests
    })


def distance(lat1, lon1, lat2, lon2):
    return math.sqrt((float(lat1)-float(lat2))**2 + (float(lon1)-float(lon2))**2)





def search(request):
    if request.method == 'POST':
        blood_group = request.POST.get('blood_group')
        location = request.POST.get('location')
        lat = request.POST.get('latitude')
        lon = request.POST.get('longitude')

        #  Convert lat/lon to float safely
        try:
            lat = float(lat) if lat else None
            lon = float(lon) if lon else None
        except:
            lat, lon = None, None

        donors = Donor.objects.all()

        result = []

        for d in donors:

            #  ELIGIBILITY CHECK (90 days rule)
            if d.last_donation_date:
                next_date = d.last_donation_date + timedelta(days=90)
                if timezone.now().date() < next_date:
                    continue   # skip not eligible

            #  BLOOD GROUP FILTER
            if blood_group and d.blood_group != blood_group:
                continue

            # LOCATION FILTER
            if location and location.lower() not in d.location.lower():
                continue

            # DISTANCE CALCULATION
            if d.latitude and d.longitude and lat and lon:
                dist = distance(lat, lon, d.latitude, d.longitude)
            else:
                dist = None

            result.append({
                'donor': d,
                'distance': dist
            })

        #  SORT BY DISTANCE
        result.sort(key=lambda x: x['distance'] if x['distance'] is not None else 9999)

        #  MARK NEAREST
        if result:
            result[0]['nearest'] = True

        return render(request, 'results.html', {'donors': result})

    return render(request, 'search.html')

def compatible_donors(group):
    return {
        "A+": ["A+", "A-", "O+", "O-"],
        "A-": ["A-", "O-"],
        "B+": ["B+", "B-", "O+", "O-"],
        "B-": ["B-", "O-"],
        "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
        "AB-": ["A-", "B-", "AB-", "O-"],
        "O+": ["O+", "O-"],
        "O-": ["O-"],
    }.get(group, [])


def send_reminder(request_id):
    time.sleep(300)  # ⏳ 5 minutes (change to 3600 = 1 hour later)

    try:
        req = BloodRequest.objects.get(id=request_id)
    except:
        return

    # ❌ If already fulfilled → stop
    if req.status == 'fulfilled':
        return

    donors = Donor.objects.all()

    for donor in donors:

        # 🩸 Blood match
        if donor.blood_group != req.blood_group:
            continue

        # 📍 Location match
        if req.location and req.location.lower() not in donor.location.lower():
            continue

        # ✅ Eligibility check
        if donor.last_donation_date:
            next_date = donor.last_donation_date + timedelta(days=90)
            if timezone.now().date() < next_date:
                continue

        # 📧 Send reminder
        if donor.user.email:
            send_mail(
                subject="⏰ Reminder: Blood Still Needed",
                message=f"""
Reminder 🚨

Blood Group: {req.blood_group}
Location: {req.location}

This request is still pending.

Please help if possible ❤️

- LifeLink Team
""",
                from_email=None,
                recipient_list=[donor.user.email],
                fail_silently=True,
            )


def view_requests(request):
    requests = BloodRequest.objects.all().order_by('-id')
    return render(request, 'view_requests.html', {'requests': requests})


def register_hospital(request):
    form = HospitalRegisterForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():

        username = form.cleaned_data['username']

        # 🔥 CHECK IF USERNAME EXISTS
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another.")
            return render(request, 'register_hospital.html', {'form': form})

        # ✅ CREATE USER
        user = User.objects.create_user(
            username=username,
            password=form.cleaned_data['password']
        )

        # ✅ SAVE HOSPITAL
        hospital = form.save(commit=False)
        hospital.user = user
        hospital.save()

        messages.success(request, "Hospital registered successfully!")

        return redirect('login')

    return render(request, 'register_hospital.html', {'form': form})



@login_required
def profile(request):
    user = request.user

    donor = None
    hospital = None

    # Check role
    if Donor.objects.filter(user=user).exists():
        donor = Donor.objects.get(user=user)

    if Hospital.objects.filter(user=user).exists():
        hospital = Hospital.objects.get(user=user)

    return render(request, 'profile.html', {
        'donor': donor,
        'hospital': hospital
    })




def is_eligible(donor):
    if donor.last_donation_date:
        return timezone.now().date() >= donor.last_donation_date + timedelta(days=90)
    return True  # If never donated → eligible



@login_required
def update_donation(request):
    donor = Donor.objects.get(user=request.user)

    donor.last_donation_date = timezone.now().date()
    donor.save()

    return redirect('dashboard')

@login_required
def donate_today(request):
    donor = Donor.objects.get(user=request.user)

    donor.last_donation_date = timezone.now().date()
    donor.save()

    return redirect('dashboard')



def contact_donor(request, donor_id):
    donor = Donor.objects.get(id=donor_id)

    if request.method == "POST":
        message = request.POST.get('message')

        send_mail(
            subject="Blood Request",
            message=message,
            from_email="hospital@example.com",
            recipient_list=[donor.user.email],
        )

        messages.success(request, "Email sent successfully!")

    return redirect('search')



@login_required
def mark_donated(request, request_id):

    req = get_object_or_404(BloodRequest, id=request_id)
    donor = get_object_or_404(Donor, user=request.user)

    # 🔥 ELIGIBILITY CHECK (90 days rule)
    if donor.last_donation_date:
        next_date = donor.last_donation_date + timedelta(days=90)

        if timezone.now().date() < next_date:
            messages.error(request, "You are not eligible to donate yet.")
            return redirect('donor_requests')

    # ❌ Prevent double fulfillment
    if req.status == 'fulfilled':
        messages.warning(request, "This request is already fulfilled.")
        return redirect('dashboard')

    # ✅ Mark fulfilled + store donor
    req.status = 'fulfilled'
    req.fulfilled_by = donor
    req.save()

    # 🔥 VERY IMPORTANT: UPDATE DONOR LAST DONATION DATE
    donor.last_donation_date = timezone.now().date()
    donor.save()

    # ❤️ THANK YOU EMAIL (to donor)
    if donor.user.email:
        send_mail(
            subject="❤️ Thank You for Saving a Life",
            message=f"""
Dear {donor.user.username},

Thank you for donating blood 🩸

You helped save a life ❤️

You can donate again after 90 days.

- LifeLink Team
""",
            from_email=None,
            recipient_list=[donor.user.email],
            fail_silently=True,
        )

    # 📢 INFORM OTHER DONORS
    other_donors = Donor.objects.exclude(id=donor.id)

    for d in other_donors:
        if d.user.email:
            send_mail(
                subject="✅ Request Fulfilled",
                message=f"""
Good news 🎉

The blood request ({req.blood_group}) at {req.location} has been fulfilled.

Thank you for your willingness to help 🙏

- LifeLink Team
""",
                from_email=None,
                recipient_list=[d.user.email],
                fail_silently=True,
            )

    messages.success(request, "Thank you! You can donate again after 90 days.")

    return redirect('dashboard')


@login_required
def confirm_request(request, request_id, donor_id):
    req = BloodRequest.objects.get(id=request_id)
    donor = Donor.objects.get(id=donor_id)

    # Prevent double update
    if req.status == 'fulfilled':
        messages.warning(request, "Already fulfilled")
        return redirect('dashboard')

    req.status = 'fulfilled'
    req.fulfilled_by = donor
    req.save()

    messages.success(request, "Request marked as fulfilled")

    return redirect('dashboard')


@login_required
def request_history(request):
    hospital = Hospital.objects.get(user=request.user)

    requests = BloodRequest.objects.filter(
        hospital=hospital
    ).order_by('-created_at')

    return render(request, 'request_history.html', {
        'requests': requests
    })


@login_required
def donor_history(request):
    donor = Donor.objects.get(user=request.user)

    donations = BloodRequest.objects.filter(
        fulfilled_by=donor
    ).order_by('-created_at')

    return render(request, 'donor_history.html', {
        'donations': donations,
        'count': donations.count()
    })


@login_required
def donor_requests(request):
    donor = Donor.objects.get(user=request.user)

    requests = BloodRequest.objects.filter(status='pending').order_by('-created_at')

    # 🔥 ADD THIS
    days_left = None

    if donor.last_donation_date:
        next_date = donor.last_donation_date + timedelta(days=90)
        today = timezone.now().date()

        if today < next_date:
            days_left = (next_date - today).days

    return render(request, 'donor_requests.html', {
        'requests': requests,
        'days_left': days_left   # 🔥 IMPORTANT
    })


def get_donor_phases(blood_group):
    return {
        "A+": [
            ["A+"],
            ["A-", "O+", "O-"]
        ],
        "B+": [
            ["B+"],
            ["B-", "O+", "O-"]
        ],
        "AB+": [
            ["AB+"],
            ["A+", "B+", "O+"],
            ["A-", "B-", "O-"]
        ],
        "O+": [
            ["O+"],
            ["O-"]
        ],
        "A-": [
            ["A-"],
            ["O-"]
        ],
        "B-": [
            ["B-"],
            ["O-"]
        ],
        "AB-": [
            ["AB-"],
            ["A-", "B-", "O-"]
        ],
        "O-": [
            ["O-"]
        ]
    }.get(blood_group, [])



# ================= PHASE FUNCTION =================
def send_phase_emails(request_id, phases, location):

    # ⏱ Phase delays (in seconds)
    # 6 hours = 21600 sec
    # 12 hours = 43200 sec
    phase_delays = [21600, 21600]

    for i in range(1, len(phases)):

        # 🔥 Wait based on phase
        time.sleep(phase_delays[i-1])

        try:
            req = BloodRequest.objects.get(id=request_id)
        except:
            return

        # ❌ Stop if already fulfilled
        if req.status == 'fulfilled':
            return

        group_list = phases[i]

        donors = Donor.objects.filter(blood_group__in=group_list)

        for donor in donors:

            # 📍 Location filter
            if location and location.lower() not in donor.location.lower():
                continue

            # ✅ Eligibility check
            if donor.last_donation_date:
                next_date = donor.last_donation_date + timedelta(days=90)
                if timezone.now().date() < next_date:
                    continue

            if donor.user.email:
                send_mail(
                    subject="⚠️ Urgent Blood Requirement",
                    message=f"""
🚨 BLOOD REQUEST (Phase {i+1})

Blood Group: {req.blood_group}
Location: {req.location}

Still not fulfilled. Please help if possible ❤️

- LifeLink Team
""",
                    from_email=None,
                    recipient_list=[donor.user.email],
                    fail_silently=True,
                )


# ================= CREATE REQUEST (UPDATED) =================
def create_request(request):
    if request.method == "POST":
        blood_group = request.POST.get('blood_group')
        location = request.POST.get('location')

        hospital = Hospital.objects.get(user=request.user)

        # 🔥 SAVE REQUEST
        req = BloodRequest.objects.create(
            hospital=hospital,
            blood_group=blood_group,
            location=location,
            status='pending'
        )

        phases = get_donor_phases(blood_group)

        notified_count = 0

        # ================= PHASE 1 =================
        first_phase = phases[0]

        donors = Donor.objects.filter(blood_group__in=first_phase)

        valid_donors = []

        for donor in donors:

            # 📍 Location filter
            if location and location.lower() not in donor.location.lower():
                continue

            # ✅ Eligibility check
            if donor.last_donation_date:
                next_date = donor.last_donation_date + timedelta(days=90)
                if timezone.now().date() < next_date:
                    continue

            valid_donors.append(donor)

        # 🔥 CASE 1: PHASE 1 DONORS AVAILABLE
        if valid_donors:

            for donor in valid_donors:
                if donor.user.email:
                    send_mail(
                        subject="🚨 Urgent Blood Request",
                        message=f"""
🚨 URGENT BLOOD REQUEST (Priority)

Blood Group: {blood_group}
Location: {location}

Please help save a life ❤️

- LifeLink Team
""",
                        from_email=None,
                        recipient_list=[donor.user.email],
                        fail_silently=True,
                    )
                    notified_count += 1

            # 🔥 Start Phase 2 & 3 normally
            threading.Thread(
                target=send_phase_emails,
                args=(req.id, phases, location)
            ).start()

            messages.success(
                request,
                f"Phase 1 complete! {notified_count} donors notified."
            )

        # 🔥 CASE 2: NO PHASE 1 DONORS → SKIP
        else:

            # Skip first phase → start from phase 2 immediately
            threading.Thread(
                target=send_phase_emails,
                args=(req.id, phases[1:], location)
            ).start()

            messages.warning(
                request,
                "No exact match donors found. Moving to compatible donors immediately."
            )

        return redirect('dashboard')

    return render(request, 'create_request.html')