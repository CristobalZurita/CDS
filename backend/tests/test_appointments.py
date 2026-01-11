"""
Tests for Appointment System
Unit tests for models, schemas, CRUD operations, and endpoints
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from backend.app.models.appointment import Appointment
from backend.app.schemas.appointment import AppointmentCreate, AppointmentResponse
from backend.app.crud.appointment import (
    create_appointment,
    get_appointment,
    get_appointments,
    get_appointments_by_email,
    delete_appointment
)


class TestAppointmentModel:
    """Test Appointment SQLAlchemy model"""
    
    def test_appointment_creation(self):
        """Test creating appointment instance"""
        apt = Appointment(
            nombre="Juan García",
            email="juan@example.com",
            telefono="+56912345678",
            fecha=datetime.now() + timedelta(days=1),
            mensaje="Test appointment"
        )
        
        assert apt.nombre == "Juan García"
        assert apt.email == "juan@example.com"
        assert apt.estado == "pendiente"
        assert apt.notificacion_enviada == False
    
    def test_appointment_to_dict(self):
        """Test appointment serialization"""
        apt = Appointment(
            id=1,
            nombre="Test User",
            email="test@example.com",
            telefono="+56912345678",
            fecha=datetime.now(),
            estado="confirmado"
        )
        
        data = apt.to_dict()
        assert data['nombre'] == "Test User"
        assert data['estado'] == "confirmado"
        assert 'created_at' in data


class TestAppointmentSchema:
    """Test Pydantic schemas and validation"""
    
    def test_valid_appointment_creation(self):
        """Test valid appointment data"""
        future_date = datetime.now() + timedelta(days=1)
        
        apt = AppointmentCreate(
            nombre="Juan García Pérez",
            email="juan@example.com",
            telefono="+56912345678",
            fecha=future_date,
            mensaje="Test message"
        )
        
        assert apt.nombre == "Juan García Pérez"
        assert apt.email == "juan@example.com"
    
    def test_invalid_nombre_with_numbers(self):
        """Test nombre validation rejects numbers"""
        future_date = datetime.now() + timedelta(days=1)
        
        with pytest.raises(ValueError):
            AppointmentCreate(
                nombre="Juan123",
                email="juan@example.com",
                telefono="+56912345678",
                fecha=future_date
            )
    
    def test_invalid_nombre_special_chars(self):
        """Test nombre validation rejects special characters"""
        future_date = datetime.now() + timedelta(days=1)
        
        with pytest.raises(ValueError):
            AppointmentCreate(
                nombre="Juan@García",
                email="juan@example.com",
                telefono="+56912345678",
                fecha=future_date
            )
    
    def test_valid_nombre_with_accents(self):
        """Test nombre allows accents"""
        future_date = datetime.now() + timedelta(days=1)
        
        apt = AppointmentCreate(
            nombre="Juan José García Pérez",
            email="juan@example.com",
            telefono="+56912345678",
            fecha=future_date
        )
        
        assert "José" in apt.nombre
        assert "García" in apt.nombre
    
    def test_valid_nombre_with_ñ(self):
        """Test nombre allows Ñ"""
        future_date = datetime.now() + timedelta(days=1)
        
        apt = AppointmentCreate(
            nombre="Peña González Niño",
            email="test@example.com",
            telefono="+56912345678",
            fecha=future_date
        )
        
        assert "Peña" in apt.nombre
    
    def test_invalid_email_format(self):
        """Test email validation"""
        future_date = datetime.now() + timedelta(days=1)
        
        with pytest.raises(ValueError):
            AppointmentCreate(
                nombre="Juan García",
                email="invalid-email",
                telefono="+56912345678",
                fecha=future_date
            )
    
    def test_invalid_telefono_no_plus(self):
        """Test telefono must start with +"""
        future_date = datetime.now() + timedelta(days=1)
        
        with pytest.raises(ValueError):
            AppointmentCreate(
                nombre="Juan García",
                email="juan@example.com",
                telefono="56912345678",  # Missing +
                fecha=future_date
            )
    
    def test_invalid_telefono_with_letters(self):
        """Test telefono rejects letters"""
        future_date = datetime.now() + timedelta(days=1)
        
        with pytest.raises(ValueError):
            AppointmentCreate(
                nombre="Juan García",
                email="juan@example.com",
                telefono="+5691234567A",
                fecha=future_date
            )
    
    def test_invalid_past_fecha(self):
        """Test fecha must be in future"""
        past_date = datetime.now() - timedelta(days=1)
        
        with pytest.raises(ValueError):
            AppointmentCreate(
                nombre="Juan García",
                email="juan@example.com",
                telefono="+56912345678",
                fecha=past_date
            )
    
    def test_mensaje_optional(self):
        """Test mensaje is optional"""
        future_date = datetime.now() + timedelta(days=1)
        
        apt = AppointmentCreate(
            nombre="Juan García",
            email="juan@example.com",
            telefono="+56912345678",
            fecha=future_date
        )
        
        assert apt.mensaje is None


class TestAppointmentCRUD:
    """Test CRUD operations (requires database)"""
    
    @pytest.mark.asyncio
    async def test_create_appointment(self, db: Session):
        """Test creating appointment in database"""
        apt_data = AppointmentCreate(
            nombre="Test User",
            email="test@example.com",
            telefono="+56912345678",
            fecha=datetime.now() + timedelta(days=1),
            mensaje="Test appointment"
        )
        
        db_apt = await create_appointment(db, apt_data)
        
        assert db_apt.id is not None
        assert db_apt.nombre == "Test User"
        assert db_apt.estado == "pendiente"
    
    @pytest.mark.asyncio
    async def test_get_appointment(self, db: Session):
        """Test retrieving appointment"""
        apt_data = AppointmentCreate(
            nombre="Test User",
            email="test@example.com",
            telefono="+56912345678",
            fecha=datetime.now() + timedelta(days=1)
        )
        
        created = await create_appointment(db, apt_data)
        retrieved = await get_appointment(db, created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.nombre == "Test User"
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_appointment(self, db: Session):
        """Test getting non-existent appointment returns None"""
        apt = await get_appointment(db, 99999)
        assert apt is None
    
    @pytest.mark.asyncio
    async def test_delete_appointment(self, db: Session):
        """Test deleting appointment"""
        apt_data = AppointmentCreate(
            nombre="Test User",
            email="test@example.com",
            telefono="+56912345678",
            fecha=datetime.now() + timedelta(days=1)
        )
        
        created = await create_appointment(db, apt_data)
        deleted = await delete_appointment(db, created.id)
        
        assert deleted is True
        retrieved = await get_appointment(db, created.id)
        assert retrieved is None


class TestAppointmentAPI:
    """Test API endpoints"""
    
    def test_create_appointment_endpoint(self, client: TestClient):
        """Test POST /appointments/"""
        response = client.post(
            "/api/v1/appointments/",
            json={
                "nombre": "Test User",
                "email": "test@example.com",
                "telefono": "+56912345678",
                "fecha": (datetime.now() + timedelta(days=1)).isoformat(),
                "mensaje": "Test appointment"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data['nombre'] == "Test User"
        assert data['estado'] == "pendiente"
        assert 'id' in data
    
    def test_create_appointment_invalid_nombre(self, client: TestClient):
        """Test POST with invalid nombre"""
        response = client.post(
            "/api/v1/appointments/",
            json={
                "nombre": "Test123",
                "email": "test@example.com",
                "telefono": "+56912345678",
                "fecha": (datetime.now() + timedelta(days=1)).isoformat()
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_get_appointments_endpoint(self, client: TestClient):
        """Test GET /appointments/"""
        response = client.get("/api/v1/appointments/")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_appointment_by_email_endpoint(self, client: TestClient):
        """Test GET /appointments/email/{email}"""
        response = client.get("/api/v1/appointments/email/test@example.com")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_pending_appointments(self, client: TestClient):
        """Test GET /appointments/status/pending"""
        response = client.get("/api/v1/appointments/status/pending")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)


# Fixtures for testing

@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def db():
    """Create test database session"""
    # This would be configured with a test database
    pass
