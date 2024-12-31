from django.db import models

class UserTypes(models.TextChoices):
    # Roles principales
    ADMIN = 'ADMIN', 'Administrador'
    DOCTOR = 'DOCTOR', 'Doctor'
    PATIENT = 'PATIENT', 'Paciente'
    
    # Tipos de profesionales
    NUTRITIONIST = 'NUTRITIONIST', 'Nutricionista'
    PHYSIOTHERAPIST = 'PHYSIOTHERAPIST', 'Fisioterapeuta'
    PSYCHOLOGIST = 'PSYCHOLOGIST', 'Psicólogo'
    NURSE = 'NURSE', 'Enfermero'
    DENTIST = 'DENTIST', 'Dentista'
    CARDIOLOGIST = 'CARDIOLOGIST', 'Cardiólogo'
    PEDIATRICIAN = 'PEDIATRICIAN', 'Pediatra'
    
    # Personal administrativo
    RECEPTIONIST = 'RECEPTIONIST', 'Recepcionista'
    COORDINATOR = 'COORDINATOR', 'Coordinador'
    MANAGER = 'MANAGER', 'Gerente'

    @classmethod
    def get_professional_types(cls):
        """Retorna solo los tipos de profesionales de la salud"""
        return [
            cls.DOCTOR,
            cls.NUTRITIONIST,
            cls.PHYSIOTHERAPIST,
            cls.PSYCHOLOGIST,
            cls.NURSE,
            cls.DENTIST,
            cls.CARDIOLOGIST,
            cls.PEDIATRICIAN,
        ]

    @classmethod
    def get_staff_types(cls):
        """Retorna los tipos de personal administrativo"""
        return [
            cls.ADMIN,
            cls.RECEPTIONIST,
            cls.COORDINATOR,
            cls.MANAGER,
        ]

    @classmethod
    def is_professional(cls, user_type):
        """Verifica si un tipo de usuario es un profesional de la salud"""
        return user_type in [choice.value for choice in cls.get_professional_types()]

    @classmethod
    def is_staff(cls, user_type):
        """Verifica si un tipo de usuario es personal administrativo"""
        return user_type in [choice.value for choice in cls.get_staff_types()] 