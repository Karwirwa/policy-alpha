from datetime import datetime, timezone, timedelta

from app.db.init import init_db
from app.db.database import SessionLocal
from app.services.portfolio_service import PortfolioService
from app.services.watchlist_service import WatchlistService
from app.services.simulation_service import InvestmentSimulationService
from app.services.opportunity_history_service import OpportunityHistoryService


def main() -> None:
    init_db()

    with SessionLocal() as session:
        portfolio_svc = PortfolioService(session)
        watch_svc = WatchlistService(session)
        sim_svc = InvestmentSimulationService(session)
        hist_svc = OpportunityHistoryService(session)

        # Create sample portfolio
        p = portfolio_svc.create_portfolio("Demo Portfolio", "Seeded portfolio for testing")
        print(f"Created portfolio {p.uuid}")

        # Add Bamburi and a placeholder company
        portfolio_svc.add_company(p.uuid, "company_bamburi", 50.0, "Core infrastructure supplier")
        portfolio_svc.add_company(p.uuid, "company_acme", 50.0, "Sample manufacturer")
        print("Added companies to portfolio")

        # Create watchlist
        watch_svc.add("company_bamburi", priority=1, reason="Monitor infrastructure mentions")
        watch_svc.add("company_acme", priority=2, reason="Potential supplier")
        print("Created watchlist items")

        # Simulate buys (two simulations)
        now = datetime.now(timezone.utc)
        sim1 = sim_svc.simulate_buy("company_bamburi", now - timedelta(days=30), 10.0, 100)
        sim2 = sim_svc.simulate_buy("company_acme", now - timedelta(days=10), 5.0, 200)
        # Update current prices
        sim_svc.update_market_price(sim1.uuid, 12.5)
        sim_svc.update_market_price(sim2.uuid, 4.0)
        print("Simulations created and updated")

        # Seed historical opportunity scores
        hist_svc.save_score("company_bamburi", 72.0, "Neutral", generated_at=now - timedelta(days=60))
        hist_svc.save_score("company_bamburi", 81.0, "High Opportunity", generated_at=now - timedelta(days=30))
        hist_svc.save_score("company_bamburi", 90.0, "Strong Buy", generated_at=now - timedelta(days=1))
        hist_svc.save_score("company_acme", 50.0, "Neutral", generated_at=now - timedelta(days=15))
        print("Seeded opportunity score history")


if __name__ == "__main__":
    main()
