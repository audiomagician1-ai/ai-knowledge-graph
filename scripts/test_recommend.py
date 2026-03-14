"""Test the recommendation endpoint."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'apps', 'api'))

from db.sqlite_client import init_db
init_db()

import asyncio
from routers.learning import recommend_next

async def main():
    result = await recommend_next(5)
    print(f"Current level: {result['current_level']}, Mastered: {result['mastered_count']}/{result['total_concepts']}")
    print(f"\nTop {len(result['recommendations'])} recommendations:")
    for r in result['recommendations']:
        print(f"  {r['score']:5.1f} | Lv.{r['difficulty']} | {r['name']:25s} | {r['reason']}")

asyncio.run(main())
