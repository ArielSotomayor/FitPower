from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from database import engine
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User, UserRole, UserStatus
from schemas.user_schema import UserRegister
from utils.security import hash_password
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi import Form
from fastapi.responses import RedirectResponse
from utils.security import hash_password
from utils.email import send_verification_email
from fastapi.responses import JSONResponse
import random
from datetime import datetime, timedelta
from database import SessionLocal
from starlette.middleware.sessions import SessionMiddleware
from models.trainer import TrainerProfile
from models.trainer import TrainerSpecialty
from fastapi import UploadFile, File, Form
import shutil
from models.trainer import TrainerProfileSpecialty
app = FastAPI()

from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")


from starlette.middleware.sessions import SessionMiddleware

app.add_middleware(
    SessionMiddleware,
    secret_key="fitpowerpro_secret"
)

# conectar templates
templates = Jinja2Templates(directory="templates")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/about")
def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


from fastapi import Request, Form
from fastapi.responses import RedirectResponse
from passlib.hash import bcrypt
import mysql.connector
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Info2026/*-",
        database="fitpower_db"
    )

from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi import Form, Depends
from passlib.hash import argon2
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):

    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )

@app.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.email == email).first()

    # Usuario no existe
    if not user:
        return RedirectResponse("/login?error=user", status_code=303)

    # Contraseña incorrecta
    if not argon2.verify(password, user.password_hash):
        return RedirectResponse("/login?error=password", status_code=303)

    # Email no verificado
    if not user.is_email_verified:
        return RedirectResponse(f"/login?verify=1&email={email}", status_code=303)

    # Validaciones para entrenadores
    if user.role == "entrenador":

        if user.status == "pending":
            return RedirectResponse("/login?error=pending", status_code=303)

        if user.status == "rejected":
            return RedirectResponse("/login?error=rejected", status_code=303)

    # Guardar sesión
    request.session["user_id"] = user.id

    # Redirección según rol
    if user.role == "cliente":
        return RedirectResponse("/client/profile?success=login", status_code=303)

    if user.role == "entrenador":
        return RedirectResponse("/trainer/profile?success=login", status_code=303)

    if user.role == "admin":
        return RedirectResponse("/admin/dashboard?success=login", status_code=303)

    return RedirectResponse("/", status_code=303)

@app.get("/admin/dashboard")
def admin_dashboard(request: Request, success: str = None):
    db = next(get_db())  # <-- obtener sesión manual
    user = get_current_user(request, db)  # <-- pasar db
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse(
        "Admin Dashboard/admin_profile.html",
        {"request": request, "user": user, "success": success}
    )

# Obtener todas las especializaciones y renderizar HTML
@app.get("/admin/specialisations")
def admin_specialisations(request: Request, db: Session = Depends(get_db)):
    specialisations = db.query(TrainerSpecialty).all()
    return templates.TemplateResponse(
        "Admin Dashboard/management_specialisation.html",
        {"request": request, "specialisations": specialisations}
    )

# Agregar especialización
@app.post("/admin/specialisations/add")
def add_specialisation(name: str = Form(...), db: Session = Depends(get_db)):
    # Validar si ya existe
    existing = db.query(TrainerSpecialty).filter(TrainerSpecialty.name == name).first()
    if existing:
        return JSONResponse({"status": "error", "message": "La especialización ya existe"})
    
    new_spec = TrainerSpecialty(name=name)
    db.add(new_spec)
    db.commit()
    db.refresh(new_spec)

    return {"status": "success", "id": new_spec.id, "name": new_spec.name}

# Editar especialización
@app.post("/admin/specialisations/edit/{spec_id}")
def edit_specialisation(spec_id: int, name: str = Form(...), db: Session = Depends(get_db)):
    spec = db.query(TrainerSpecialty).filter(TrainerSpecialty.id == spec_id).first()
    if not spec:
        return JSONResponse({"status": "error", "message": "Especialización no encontrada"})
    
    # Validar duplicado
    existing = db.query(TrainerSpecialty).filter(TrainerSpecialty.name == name, TrainerSpecialty.id != spec_id).first()
    if existing:
        return JSONResponse({"status": "error", "message": "Ya existe otra especialización con ese nombre"})

    spec.name = name
    db.commit()
    db.refresh(spec)

    return {"status": "success", "id": spec.id, "name": spec.name}

# Eliminar especialización
@app.post("/admin/specialisations/delete/{spec_id}")
def delete_specialisation(spec_id: int, db: Session = Depends(get_db)):
    spec = db.query(TrainerSpecialty).filter(TrainerSpecialty.id == spec_id).first()
    if not spec:
        return JSONResponse({"status": "error", "message": "Especialización no encontrada"})

    db.delete(spec)
    db.commit()
    return {"status": "success"}

@app.get("/admin/users")
def admin_users(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).all()

    users_list = []
    for u in users:
        role_name = u.role.name if hasattr(u.role, "name") else u.role  # solo el string
        users_list.append({
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "role": role_name,
            "status": u.status
        })

    return templates.TemplateResponse(
        "Admin Dashboard/user_management.html",
        {"request": request, "users": users_list}
    )

@app.post("/admin/users/accept/{user_id}")
def accept_trainer(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return JSONResponse({"status": "error", "message": "Usuario no encontrado"})
    if user.role != "entrenador":
        return JSONResponse({"status": "error", "message": "Solo entrenadores pueden ser aceptados"})
    user.status = "approved"
    db.commit()
    return JSONResponse({"status": "success"})

@app.post("/admin/users/reject/{user_id}")
def reject_trainer(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return JSONResponse({"status": "error", "message": "Usuario no encontrado"})
    if user.role != "entrenador":
        return JSONResponse({"status": "error", "message": "Solo entrenadores pueden ser rechazados"})
    user.status = "rejected"
    db.commit()
    return JSONResponse({"status": "success"})

@app.post("/admin/users/edit/{user_id}")
def edit_user(
    user_id: int,
    full_name: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return JSONResponse({"status": "error", "message": "Usuario no encontrado"})
    user.full_name = full_name
    user.email = email
    db.commit()
    return JSONResponse({"status": "success", "full_name": full_name, "email": email})

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="templates")

@app.get("/client/profile")
def client_profile(
    request: Request,
    db: Session = Depends(get_db)
):

    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse("/login")

    user = db.query(User).filter(User.id == user_id).first()

    return templates.TemplateResponse(
        "Client Dashboard/client_profile.html",
        {
            "request": request,
            "user": user
        }
    )

def get_current_user(request: Request, db: Session = Depends(get_db)):

    user_id = request.session.get("user_id")

    if not user_id:
        return None

    return db.query(User).filter(User.id == user_id).first()

@app.get("/trainer/profile")
def trainer_profile(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    if not user:
        return RedirectResponse("/login")

    trainer = db.query(TrainerProfile).filter(
        TrainerProfile.user_id == user.id
    ).first()

    # verificar si el perfil está completo
    show_modal = False
    if trainer and trainer.profile_completed == 0:
        show_modal = True

    # 🔹 AQUÍ cargas las especialidades
    specialties = db.query(TrainerSpecialty).all()

    return templates.TemplateResponse(
        "Trainer Dashboard/trainer_profile.html",
        {
            "request": request,
            "user": user,
            "trainer": trainer,
            "show_modal": show_modal,
            "specialties": specialties  # 🔹 se envían al HTML
        }
    )


from typing import List

@app.post("/trainer/complete-profile")
async def complete_profile(
    age: int = Form(...),
    weight: float = Form(...),
    height: float = Form(...),
    gender: str = Form(...),
    phone: str = Form(...),
    location: str = Form(...),
    specialties: str = Form(...),  # ahora llega texto
    photo: UploadFile = File(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    filename = None

    if photo:
        filename = photo.filename
        with open(f"static/profile_photos/{filename}", "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)

    trainer = db.query(TrainerProfile).filter(
        TrainerProfile.user_id == user.id
    ).first()

    trainer.age = age
    trainer.weight = weight
    trainer.height = height
    trainer.gender = gender
    trainer.phone = phone
    trainer.location = location
    trainer.profile_photo = filename
    trainer.profile_completed = 1

    db.commit()

    # limpiar especialidades anteriores
    db.query(TrainerProfileSpecialty).filter(
        TrainerProfileSpecialty.trainer_id == trainer.id
    ).delete()

    db.commit()

    # convertir string a lista
    specialties_list = [s.strip() for s in specialties.split(",") if s.strip()]

    for spec_name in specialties_list:

        specialty = db.query(TrainerSpecialty).filter(
            TrainerSpecialty.name == spec_name
        ).first()

        # si no existe se crea
        if not specialty:
            specialty = TrainerSpecialty(name=spec_name)
            db.add(specialty)
            db.commit()
            db.refresh(specialty)

        link = TrainerProfileSpecialty(
            trainer_id=trainer.id,
            specialty_id=specialty.id
        )

        db.add(link)

    db.commit()

    return RedirectResponse("/trainer/profile", status_code=303)

@app.get("/trainer/profile/data")
def trainer_profile_data(
    request: Request,
    db: Session = Depends(get_db)
):

    user = get_current_user(request, db)

    if not user:
        return {"error": "not authenticated"}

    trainer = db.query(TrainerProfile).filter(
        TrainerProfile.user_id == user.id
    ).first()

    if not trainer:
        return {"error": "trainer profile not found"}

    specialties = db.query(TrainerSpecialty).join(
        TrainerProfileSpecialty,
        TrainerSpecialty.id == TrainerProfileSpecialty.specialty_id
    ).filter(
        TrainerProfileSpecialty.trainer_id == trainer.id
    ).all()

    return {
        "trainer": {
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "initials": "".join([n[0] for n in (user.full_name or "").split()]).upper(),
            "certifications": trainer.certification,
            "experience_years": trainer.experience_years,
            "bio": trainer.bio,
            "profile_photo": trainer.profile_photo
        },

        "specialties": [
            {"name": s.name}
            for s in specialties
        ]
    }

@app.post("/trainer/update-profile")
def update_profile(
    request: Request,
    weight_lbs: float = Form(None),
    height_m: float = Form(None),
    phone: str = Form(None),
    address: str = Form(None),
    bio: str = Form(None)
):

    trainer_id = request.session.get("trainer_id")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE trainers
        SET
            weight_lbs=%s,
            height_m=%s,
            phone=%s,
            address=%s,
            bio=%s
        WHERE id=%s
    """,(weight_lbs,height_m,phone,address,bio,trainer_id))

    conn.commit()

    return {"success":True}


@app.get("/trainer/register", response_class=HTMLResponse)
def trainer_register_page(request: Request):

    return templates.TemplateResponse(
        "trainer_register.html",
        {"request": request}
    )
import random
from datetime import datetime, timedelta 

@app.post("/trainer/register")
def trainer_register(
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    certification: str = Form(...),
    experience_years: int = Form(...),
    bio: str = Form(...),
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        return RedirectResponse("/trainer/register?error=email", status_code=303)

    if password != confirm_password:
        return RedirectResponse("/trainer/register?error=password", status_code=303)

    hashed_password = argon2.hash(password)

    code = str(random.randint(100000, 999999))
    expires = datetime.utcnow() + timedelta(minutes=10)

    new_user = User(
        full_name=full_name,
        email=email,
        password_hash=hashed_password,
        role="entrenador",
        status="pending",
        verification_code=code,
        verification_expires=expires,
        is_email_verified=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    trainer_profile = TrainerProfile(
        user_id=new_user.id,
        certification=certification,
        experience_years=experience_years,
        bio=bio
    )

    db.add(trainer_profile)
    db.commit()

    send_verification_email(email, code)

    return RedirectResponse(
        f"/trainer/register?verify=1&email={email}",
        status_code=303
    )

@app.get("/class")
def class_page(request: Request):
    return templates.TemplateResponse("class.html", {"request": request})


@app.get("/contact")
def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


@app.get("/feature")
def feature(request: Request):
    return templates.TemplateResponse("feature.html", {"request": request})


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("Register.html", {"request": request})

from fastapi.responses import RedirectResponse

import secrets
from utils.email import send_verification_email
@app.post("/register")
def register(
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):

    if password != confirm_password:
        return RedirectResponse("/register?error=password", status_code=303)

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return RedirectResponse("/register?error=exists", status_code=303)

    # ✅ Generamos código de 6 dígitos
    verification_code = str(random.randint(100000, 999999))

    # ✅ Expira en 10 minutos
    verification_expires = datetime.utcnow() + timedelta(minutes=10)

    new_user = User(
        full_name=full_name,
        email=email,
        password_hash=hash_password(password),
        role=UserRole.cliente,
        is_email_verified=False,
        status=UserStatus.pending,
        verification_code=verification_code,
        verification_expires=verification_expires
    )

    db.add(new_user)
    db.commit()

    # 📩 Enviamos el código por correo
    send_verification_email(email, verification_code)

    # 🔥 Abrimos el modal automáticamente
    return RedirectResponse(f"/register?verify=1&email={email}", status_code=303)

@app.post("/verify-code")
def verify_code(email: str = Form(...), code: str = Form(...), db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"status": "error", "message": "Usuario no encontrado"}

    if user.verification_code != code:
        return {"status": "error", "message": "Código incorrecto"}

    if datetime.utcnow() > user.verification_expires:
        return {"status": "error", "message": "Código expirado"}

    # marcar email verificado
    user.is_email_verified = True

    # 🔑 lógica según rol
    if user.role == "cliente":
        user.status = "active"  # cliente se activa automáticamente

    if user.role == "entrenador":
        user.status = "pending"  # entrenador espera aprobación

    user.verification_code = None
    user.verification_expires = None

    db.commit()

    return {"status": "success"}

@app.post("/resend-code")
def resend_code(email: str = Form(...), db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"status": "error", "message": "Usuario no encontrado"}

    if user.is_email_verified:
        return {"status": "error", "message": "La cuenta ya está verificada"}

    code = str(random.randint(100000, 999999))

    user.verification_code = code
    user.verification_expires = datetime.utcnow() + timedelta(minutes=10)

    db.commit()

    send_verification_email(email, code)

    return {"status": "success"}




