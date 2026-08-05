from app.db.init import init_db
from app.db.database import SessionLocal
from app.services.opportunity_scoring import OpportunityScoringService
from app.repositories.opportunity_repository import OpportunityRepository


def main() -> None:
    init_db()
    with SessionLocal() as session:
        scorer = OpportunityScoringService(session)
        repo = OpportunityRepository(session)

        # find companies in DB
        companies = session.query(app.models.company.Company).all() if False else None
        # For demo, score known company IDs used in seed data
        demo_companies = ["company_bamburi", "company_safaricom"]
        for cid in demo_companies:
            try:
                score_obj, breakdowns = scorer.score_company(cid)
            except Exception as e:
                print(f"Skipping {cid}: {e}")
                continue
            saved = repo.save_score(score_obj, breakdowns)
            print(f"Company {cid} -> score {saved.total_score:.1f} recommendation={saved.recommendation}")
            print(saved.explanation)


if __name__ == "__main__":
    main()
