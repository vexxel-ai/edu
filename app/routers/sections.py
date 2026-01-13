"""
Section and Subsection management routes.

Handles:
- Section/Subsection creation requests (users)
- Approval workflows (admins/sub-admins)
- Direct creation (admins/sub-admins)
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.auth.dependencies import get_current_user, require_sub_admin
from app.database import get_session
from app.models import (
    PendingSection,
    PendingStatus,
    PendingSubsection,
    Section,
    Subsection,
    User,
)

router = APIRouter(prefix="/sections", tags=["sections"])


# ==================== Request/Response Models ====================


class SectionCreate(BaseModel):
    """Request model for creating a section."""
    name: str
    slug: str
    description: Optional[str] = None


class SubsectionCreate(BaseModel):
    """Request model for creating a subsection."""
    name: str
    slug: str
    section_id: int
    description: Optional[str] = None


class SectionResponse(BaseModel):
    """Response model for sections."""
    id: int
    name: str
    slug: str
    description: Optional[str]
    created_at: str


class SubsectionResponse(BaseModel):
    """Response model for subsections."""
    id: int
    name: str
    slug: str
    section_id: int
    description: Optional[str]
    created_at: str


class PendingSectionResponse(BaseModel):
    """Response model for pending section requests."""
    id: int
    name: str
    slug: str
    description: Optional[str]
    status: str
    requested_by_email: str
    created_at: str
    reviewed_at: Optional[str] = None
    reviewed_by_email: Optional[str] = None
    rejection_reason: Optional[str] = None


class PendingSubsectionResponse(BaseModel):
    """Response model for pending subsection requests."""
    id: int
    name: str
    slug: str
    section_id: int
    section_name: str
    description: Optional[str]
    status: str
    requested_by_email: str
    created_at: str
    reviewed_at: Optional[str] = None
    reviewed_by_email: Optional[str] = None
    rejection_reason: Optional[str] = None


class ApprovalRequest(BaseModel):
    """Request model for approving/rejecting."""
    approved: bool
    rejection_reason: Optional[str] = None


# ==================== Public Routes (List) ====================


@router.get("/", response_model=list[SectionResponse])
async def list_sections(session: Session = Depends(get_session)):
    """
    Get all sections.

    Public endpoint - no authentication required.
    """
    sections = session.exec(select(Section).order_by(Section.name)).all()
    return [
        SectionResponse(
            id=s.id,
            name=s.name,
            slug=s.slug,
            description=s.description,
            created_at=s.created_at.isoformat(),
        )
        for s in sections
    ]


@router.get("/{section_id}/subsections", response_model=list[SubsectionResponse])
async def list_subsections(section_id: int, session: Session = Depends(get_session)):
    """
    Get all subsections for a section.

    Public endpoint - no authentication required.
    """
    # Verify section exists
    section = session.get(Section, section_id)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found",
        )

    subsections = session.exec(
        select(Subsection).where(Subsection.section_id == section_id).order_by(Subsection.name)
    ).all()

    return [
        SubsectionResponse(
            id=ss.id,
            name=ss.name,
            slug=ss.slug,
            section_id=ss.section_id,
            description=ss.description,
            created_at=ss.created_at.isoformat(),
        )
        for ss in subsections
    ]


# ==================== User Routes (Requests) ====================


@router.post("/request", response_model=PendingSectionResponse, status_code=status.HTTP_201_CREATED)
async def request_new_section(
    request: SectionCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Request a new section.

    Requires authentication. Admins/sub-admins must approve.
    """
    # Check if section already exists
    existing = session.exec(
        select(Section).where((Section.name == request.name) | (Section.slug == request.slug))
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Section with this name or slug already exists",
        )

    # Check if there's already a pending request
    pending = session.exec(
        select(PendingSection).where(
            (PendingSection.name == request.name) | (PendingSection.slug == request.slug),
            PendingSection.status == PendingStatus.PENDING,
        )
    ).first()
    if pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A pending request for this section already exists",
        )

    # Create pending section
    pending_section = PendingSection(
        name=request.name,
        slug=request.slug,
        description=request.description,
        requested_by_id=user.id,
        status=PendingStatus.PENDING,
    )
    session.add(pending_section)
    session.commit()
    session.refresh(pending_section)

    return PendingSectionResponse(
        id=pending_section.id,
        name=pending_section.name,
        slug=pending_section.slug,
        description=pending_section.description,
        status=pending_section.status.value,
        requested_by_email=user.email,
        created_at=pending_section.created_at.isoformat(),
    )


@router.post(
    "/subsections/request",
    response_model=PendingSubsectionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def request_new_subsection(
    request: SubsectionCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Request a new subsection within an existing section.

    Requires authentication. Admins/sub-admins must approve.
    """
    # Verify section exists
    section = session.get(Section, request.section_id)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found",
        )

    # Check if subsection already exists in this section
    existing = session.exec(
        select(Subsection).where(
            Subsection.section_id == request.section_id,
            (Subsection.name == request.name) | (Subsection.slug == request.slug),
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subsection with this name or slug already exists in this section",
        )

    # Check if there's already a pending request
    pending = session.exec(
        select(PendingSubsection).where(
            PendingSubsection.section_id == request.section_id,
            (PendingSubsection.name == request.name) | (PendingSubsection.slug == request.slug),
            PendingSubsection.status == PendingStatus.PENDING,
        )
    ).first()
    if pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A pending request for this subsection already exists",
        )

    # Create pending subsection
    pending_subsection = PendingSubsection(
        name=request.name,
        slug=request.slug,
        section_id=request.section_id,
        description=request.description,
        requested_by_id=user.id,
        status=PendingStatus.PENDING,
    )
    session.add(pending_subsection)
    session.commit()
    session.refresh(pending_subsection)

    return PendingSubsectionResponse(
        id=pending_subsection.id,
        name=pending_subsection.name,
        slug=pending_subsection.slug,
        section_id=pending_subsection.section_id,
        section_name=section.name,
        description=pending_subsection.description,
        status=pending_subsection.status.value,
        requested_by_email=user.email,
        created_at=pending_subsection.created_at.isoformat(),
    )


# ==================== Admin Routes (Approval) ====================


@router.get("/pending", response_model=list[PendingSectionResponse])
async def get_pending_sections(
    user: User = Depends(require_sub_admin),
    session: Session = Depends(get_session),
):
    """
    Get all pending section requests.

    Requires sub-admin or admin role.
    """
    pending = session.exec(
        select(PendingSection)
        .where(PendingSection.status == PendingStatus.PENDING)
        .order_by(PendingSection.created_at.asc())
    ).all()

    results = []
    for ps in pending:
        requested_by = session.get(User, ps.requested_by_id)
        results.append(
            PendingSectionResponse(
                id=ps.id,
                name=ps.name,
                slug=ps.slug,
                description=ps.description,
                status=ps.status.value,
                requested_by_email=requested_by.email if requested_by else "Unknown",
                created_at=ps.created_at.isoformat(),
            )
        )

    return results


@router.get("/subsections/pending", response_model=list[PendingSubsectionResponse])
async def get_pending_subsections(
    user: User = Depends(require_sub_admin),
    session: Session = Depends(get_session),
):
    """
    Get all pending subsection requests.

    Requires sub-admin or admin role.
    """
    pending = session.exec(
        select(PendingSubsection)
        .where(PendingSubsection.status == PendingStatus.PENDING)
        .order_by(PendingSubsection.created_at.asc())
    ).all()

    results = []
    for pss in pending:
        requested_by = session.get(User, pss.requested_by_id)
        section = session.get(Section, pss.section_id)
        results.append(
            PendingSubsectionResponse(
                id=pss.id,
                name=pss.name,
                slug=pss.slug,
                section_id=pss.section_id,
                section_name=section.name if section else "Unknown",
                description=pss.description,
                status=pss.status.value,
                requested_by_email=requested_by.email if requested_by else "Unknown",
                created_at=pss.created_at.isoformat(),
            )
        )

    return results


@router.post("/pending/{pending_id}/approve")
async def approve_section_request(
    pending_id: int,
    approval: ApprovalRequest,
    user: User = Depends(require_sub_admin),
    session: Session = Depends(get_session),
):
    """
    Approve or reject a pending section request.

    Requires sub-admin or admin role.
    """
    # Get pending section
    pending = session.get(PendingSection, pending_id)
    if not pending:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending section request not found",
        )

    if pending.status != PendingStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Section request has already been {pending.status.value}",
        )

    if approval.approved:
        # Check again if section exists
        existing = session.exec(
            select(Section).where((Section.name == pending.name) | (Section.slug == pending.slug))
        ).first()
        if existing:
            pending.status = PendingStatus.REJECTED
            pending.rejection_reason = "Section was created by another user"
            pending.reviewed_by_id = user.id
            pending.reviewed_at = datetime.now(timezone.utc)
            session.add(pending)
            session.commit()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Section with this name or slug already exists",
            )

        # Create the section
        new_section = Section(
            name=pending.name,
            slug=pending.slug,
            description=pending.description,
        )
        session.add(new_section)

        # Update pending status
        pending.status = PendingStatus.APPROVED
        pending.reviewed_by_id = user.id
        pending.reviewed_at = datetime.now(timezone.utc)
        session.add(pending)

        session.commit()
        session.refresh(new_section)

        return {
            "message": "Section request approved and section created",
            "section": {
                "id": new_section.id,
                "name": new_section.name,
                "slug": new_section.slug,
            },
        }
    else:
        # Reject the request
        if not approval.rejection_reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rejection reason is required when rejecting a section",
            )

        pending.status = PendingStatus.REJECTED
        pending.rejection_reason = approval.rejection_reason
        pending.reviewed_by_id = user.id
        pending.reviewed_at = datetime.now(timezone.utc)
        session.add(pending)
        session.commit()

        return {
            "message": "Section request rejected",
            "rejection_reason": approval.rejection_reason,
        }


@router.post("/subsections/pending/{pending_id}/approve")
async def approve_subsection_request(
    pending_id: int,
    approval: ApprovalRequest,
    user: User = Depends(require_sub_admin),
    session: Session = Depends(get_session),
):
    """
    Approve or reject a pending subsection request.

    Requires sub-admin or admin role.
    """
    # Get pending subsection
    pending = session.get(PendingSubsection, pending_id)
    if not pending:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending subsection request not found",
        )

    if pending.status != PendingStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Subsection request has already been {pending.status.value}",
        )

    if approval.approved:
        # Check again if subsection exists
        existing = session.exec(
            select(Subsection).where(
                Subsection.section_id == pending.section_id,
                (Subsection.name == pending.name) | (Subsection.slug == pending.slug),
            )
        ).first()
        if existing:
            pending.status = PendingStatus.REJECTED
            pending.rejection_reason = "Subsection was created by another user"
            pending.reviewed_by_id = user.id
            pending.reviewed_at = datetime.now(timezone.utc)
            session.add(pending)
            session.commit()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subsection with this name or slug already exists in this section",
            )

        # Create the subsection
        new_subsection = Subsection(
            name=pending.name,
            slug=pending.slug,
            section_id=pending.section_id,
            description=pending.description,
        )
        session.add(new_subsection)

        # Update pending status
        pending.status = PendingStatus.APPROVED
        pending.reviewed_by_id = user.id
        pending.reviewed_at = datetime.now(timezone.utc)
        session.add(pending)

        session.commit()
        session.refresh(new_subsection)

        return {
            "message": "Subsection request approved and subsection created",
            "subsection": {
                "id": new_subsection.id,
                "name": new_subsection.name,
                "slug": new_subsection.slug,
                "section_id": new_subsection.section_id,
            },
        }
    else:
        # Reject the request
        if not approval.rejection_reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rejection reason is required when rejecting a subsection",
            )

        pending.status = PendingStatus.REJECTED
        pending.rejection_reason = approval.rejection_reason
        pending.reviewed_by_id = user.id
        pending.reviewed_at = datetime.now(timezone.utc)
        session.add(pending)
        session.commit()

        return {
            "message": "Subsection request rejected",
            "rejection_reason": approval.rejection_reason,
        }


# ==================== Admin Routes (Direct Creation) ====================


@router.post("/create-direct", response_model=SectionResponse)
async def create_section_direct(
    request: SectionCreate,
    user: User = Depends(require_sub_admin),
    session: Session = Depends(get_session),
):
    """
    Create a section directly without approval process.

    Only available to sub-admins and admins.
    """
    # Check if section already exists
    existing = session.exec(
        select(Section).where((Section.name == request.name) | (Section.slug == request.slug))
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Section with this name or slug already exists",
        )

    # Create section directly
    new_section = Section(
        name=request.name,
        slug=request.slug,
        description=request.description,
    )
    session.add(new_section)
    session.commit()
    session.refresh(new_section)

    return SectionResponse(
        id=new_section.id,
        name=new_section.name,
        slug=new_section.slug,
        description=new_section.description,
        created_at=new_section.created_at.isoformat(),
    )


@router.post("/subsections/create-direct", response_model=SubsectionResponse)
async def create_subsection_direct(
    request: SubsectionCreate,
    user: User = Depends(require_sub_admin),
    session: Session = Depends(get_session),
):
    """
    Create a subsection directly without approval process.

    Only available to sub-admins and admins.
    """
    # Verify section exists
    section = session.get(Section, request.section_id)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found",
        )

    # Check if subsection already exists in this section
    existing = session.exec(
        select(Subsection).where(
            Subsection.section_id == request.section_id,
            (Subsection.name == request.name) | (Subsection.slug == request.slug),
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subsection with this name or slug already exists in this section",
        )

    # Create subsection directly
    new_subsection = Subsection(
        name=request.name,
        slug=request.slug,
        section_id=request.section_id,
        description=request.description,
    )
    session.add(new_subsection)
    session.commit()
    session.refresh(new_subsection)

    return SubsectionResponse(
        id=new_subsection.id,
        name=new_subsection.name,
        slug=new_subsection.slug,
        section_id=new_subsection.section_id,
        description=new_subsection.description,
        created_at=new_subsection.created_at.isoformat(),
    )
