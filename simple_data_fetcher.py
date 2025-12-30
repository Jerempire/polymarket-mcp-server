#!/usr/bin/env python3
"""
Simple Market Data Fetcher - Multiple Output Formats
Choose how you want to see the data!
"""
import asyncio
import sys
import csv
import json
from datetime import datetime

sys.path.insert(0, 'src')
from polymarket_mcp.tools import market_discovery, market_analysis


# ============================================================================
# FORMAT 1: Simple Summary (Easy to Read)
# ============================================================================

async def get_simple_summary(query=None, limit=5):
    """Simple, clean summary format"""
    print("\n" + "="*60)
    print("📊 POLYMARKET SIMPLE SUMMARY")
    print("="*60)

    if query:
        markets = await market_discovery.search_markets(query, limit=limit)
        print(f"\n🔍 Search: '{query}'")
    else:
        markets = await market_discovery.get_trending_markets(limit=limit)
        print(f"\n🔥 Top {limit} Trending Markets")

    print(f"✅ Found {len(markets)} markets\n")

    for i, market in enumerate(markets, 1):
        question = market.get('question', 'Unknown')
        volume = market.get('volume24hr', 0) or 0
        liquidity = market.get('liquidity', 0) or 0

        print(f"{i}. {question[:70]}")
        print(f"   💰 Volume: ${volume:,.0f}")
        print(f"   💧 Liquid: ${liquidity:,.0f}")

        # Get YES/NO prices if available
        tokens = market.get('tokens', [])
        if len(tokens) >= 2:
            try:
                yes_token = tokens[0]
                price_data = await market_analysis.get_current_price(
                    token_id=yes_token.get('token_id'),
                    side="BOTH"
                )
                yes_prob = price_data.mid * 100 if price_data.mid else 0
                no_prob = 100 - yes_prob
                print(f"   📈 YES: {yes_prob:.1f}% | NO: {no_prob:.1f}%")
            except:
                pass

        print()


# ============================================================================
# FORMAT 2: CSV Export (For Excel/Sheets)
# ============================================================================

async def export_to_csv(query=None, limit=20, filename="polymarket_data.csv"):
    """Export data to CSV file"""
    print(f"\n📊 Exporting to CSV: {filename}")

    if query:
        markets = await market_discovery.search_markets(query, limit=limit)
    else:
        markets = await market_discovery.get_trending_markets(limit=limit)

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            'Question',
            'Volume 24h',
            'Liquidity',
            'YES Probability',
            'NO Probability',
            'Market ID',
            'Active',
            'Category'
        ])

        # Data
        for market in markets:
            question = market.get('question', 'Unknown')
            volume = market.get('volume24hr', 0) or 0
            liquidity = market.get('liquidity', 0) or 0
            market_id = market.get('id', '')
            active = market.get('active', False)
            tags = ', '.join(market.get('tags', []))

            # Try to get probabilities
            yes_prob = ''
            no_prob = ''
            tokens = market.get('tokens', [])
            if len(tokens) >= 2:
                try:
                    yes_token = tokens[0]
                    price_data = await market_analysis.get_current_price(
                        token_id=yes_token.get('token_id'),
                        side="BOTH"
                    )
                    yes_prob = f"{price_data.mid * 100:.1f}%" if price_data.mid else ''
                    no_prob = f"{(1 - price_data.mid) * 100:.1f}%" if price_data.mid else ''
                except:
                    pass

            writer.writerow([
                question,
                f"${volume:,.2f}",
                f"${liquidity:,.2f}",
                yes_prob,
                no_prob,
                market_id,
                active,
                tags
            ])

    print(f"✅ Exported {len(markets)} markets to {filename}")
    print(f"📂 Open in Excel or Google Sheets!\n")


# ============================================================================
# FORMAT 3: JSON Export (For Programming)
# ============================================================================

async def export_to_json(query=None, limit=20, filename="polymarket_data.json"):
    """Export data to JSON file"""
    print(f"\n📊 Exporting to JSON: {filename}")

    if query:
        markets = await market_discovery.search_markets(query, limit=limit)
    else:
        markets = await market_discovery.get_trending_markets(limit=limit)

    # Enhanced data with probabilities
    enhanced_markets = []

    for market in markets:
        market_data = {
            'question': market.get('question', 'Unknown'),
            'market_id': market.get('id', ''),
            'volume_24h': market.get('volume24hr', 0) or 0,
            'liquidity': market.get('liquidity', 0) or 0,
            'active': market.get('active', False),
            'tags': market.get('tags', []),
            'end_date': market.get('endDate') or market.get('end_date_iso'),
        }

        # Try to get probabilities
        tokens = market.get('tokens', [])
        if len(tokens) >= 2:
            try:
                yes_token = tokens[0]
                price_data = await market_analysis.get_current_price(
                    token_id=yes_token.get('token_id'),
                    side="BOTH"
                )
                market_data['yes_probability'] = price_data.mid * 100 if price_data.mid else None
                market_data['no_probability'] = (1 - price_data.mid) * 100 if price_data.mid else None
                market_data['bid'] = price_data.bid if price_data.bid else None
                market_data['ask'] = price_data.ask if price_data.ask else None
            except:
                pass

        enhanced_markets.append(market_data)

    # Write to file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'count': len(enhanced_markets),
            'markets': enhanced_markets
        }, f, indent=2)

    print(f"✅ Exported {len(enhanced_markets)} markets to {filename}")
    print(f"📂 Use in Python, JavaScript, or any JSON reader!\n")


# ============================================================================
# FORMAT 4: One-Line Per Market (Ultra Compact)
# ============================================================================

async def get_compact_list(query=None, limit=10):
    """Ultra compact - one line per market"""
    print("\n📊 COMPACT LIST\n")

    if query:
        markets = await market_discovery.search_markets(query, limit=limit)
    else:
        markets = await market_discovery.get_trending_markets(limit=limit)

    for i, market in enumerate(markets, 1):
        question = market.get('question', 'Unknown')[:60]
        volume = market.get('volume24hr', 0) or 0

        # Try to get YES probability
        prob = "?"
        tokens = market.get('tokens', [])
        if len(tokens) >= 2:
            try:
                yes_token = tokens[0]
                price_data = await market_analysis.get_current_price(
                    token_id=yes_token.get('token_id'),
                    side="BOTH"
                )
                prob = f"{price_data.mid * 100:.0f}%" if price_data.mid else "?"
            except:
                pass

        print(f"{i:2d}. [{prob:>4}] ${volume/1000:>6.0f}k - {question}")

    print()


# ============================================================================
# FORMAT 5: Only Top Opportunities (AI Filtered)
# ============================================================================

async def get_top_opportunities(limit=10):
    """Show only markets with BUY recommendations"""
    print("\n🎯 TOP TRADING OPPORTUNITIES\n")

    markets = await market_discovery.get_trending_markets(limit=limit*2)

    opportunities = []

    for market in markets:
        market_id = market.get('id') or market.get('market_id')

        try:
            analysis = await market_analysis.analyze_market_opportunity(market_id)

            if analysis.recommendation == "BUY" and analysis.confidence_score > 60:
                opportunities.append({
                    'question': market.get('question'),
                    'recommendation': analysis.recommendation,
                    'confidence': analysis.confidence_score,
                    'reasoning': analysis.reasoning,
                    'volume': market.get('volume24hr', 0) or 0
                })
        except:
            continue

    # Sort by confidence
    opportunities.sort(key=lambda x: x['confidence'], reverse=True)

    if opportunities:
        for i, opp in enumerate(opportunities[:limit], 1):
            print(f"{i}. {opp['question'][:65]}")
            print(f"   ⭐ {opp['recommendation']} - Confidence: {opp['confidence']}%")
            print(f"   💡 {opp['reasoning'][:80]}")
            print(f"   💰 Volume: ${opp['volume']:,.0f}\n")
    else:
        print("No strong BUY opportunities found right now.\n")


# ============================================================================
# Interactive Menu
# ============================================================================

async def interactive_menu():
    """Interactive menu to choose format"""
    while True:
        print("\n" + "="*60)
        print("🎯 POLYMARKET DATA FORMATS - Choose Your Style")
        print("="*60)
        print("\n1. Simple Summary (Easy to read)")
        print("2. CSV Export (For Excel/Sheets)")
        print("3. JSON Export (For programming)")
        print("4. Compact List (One line per market)")
        print("5. Top Opportunities (AI filtered BUY recommendations)")
        print("6. Custom Search (Search specific topic)")
        print("0. Exit")

        choice = input("\n👉 Enter your choice (0-6): ").strip()

        if choice == '0':
            print("\n✅ Goodbye!\n")
            break

        elif choice == '1':
            await get_simple_summary()
            input("\nPress Enter to continue...")

        elif choice == '2':
            filename = input("📂 Filename (default: polymarket_data.csv): ").strip()
            if not filename:
                filename = "polymarket_data.csv"
            await export_to_csv(filename=filename)
            input("\nPress Enter to continue...")

        elif choice == '3':
            filename = input("📂 Filename (default: polymarket_data.json): ").strip()
            if not filename:
                filename = "polymarket_data.json"
            await export_to_json(filename=filename)
            input("\nPress Enter to continue...")

        elif choice == '4':
            await get_compact_list()
            input("\nPress Enter to continue...")

        elif choice == '5':
            await get_top_opportunities()
            input("\nPress Enter to continue...")

        elif choice == '6':
            query = input("🔍 Search for: ").strip()
            if query:
                print("\nChoose format:")
                print("1. Simple Summary")
                print("2. CSV Export")
                print("3. JSON Export")
                print("4. Compact List")
                fmt = input("Format (1-4): ").strip()

                if fmt == '1':
                    await get_simple_summary(query=query)
                elif fmt == '2':
                    await export_to_csv(query=query)
                elif fmt == '3':
                    await export_to_json(query=query)
                elif fmt == '4':
                    await get_compact_list(query=query)

            input("\nPress Enter to continue...")

        else:
            print("❌ Invalid choice. Try again.")


# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """Main entry point"""

    # Check if command line arguments provided
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()

        if cmd == 'simple':
            query = sys.argv[2] if len(sys.argv) > 2 else None
            await get_simple_summary(query=query)

        elif cmd == 'csv':
            query = sys.argv[2] if len(sys.argv) > 2 else None
            filename = sys.argv[3] if len(sys.argv) > 3 else "polymarket_data.csv"
            await export_to_csv(query=query, filename=filename)

        elif cmd == 'json':
            query = sys.argv[2] if len(sys.argv) > 2 else None
            filename = sys.argv[3] if len(sys.argv) > 3 else "polymarket_data.json"
            await export_to_json(query=query, filename=filename)

        elif cmd == 'compact':
            query = sys.argv[2] if len(sys.argv) > 2 else None
            await get_compact_list(query=query)

        elif cmd == 'opportunities':
            await get_top_opportunities()

        else:
            print("Usage:")
            print("  python simple_data_fetcher.py simple [query]")
            print("  python simple_data_fetcher.py csv [query] [filename]")
            print("  python simple_data_fetcher.py json [query] [filename]")
            print("  python simple_data_fetcher.py compact [query]")
            print("  python simple_data_fetcher.py opportunities")
            print("\nOr run without arguments for interactive menu")

    else:
        # Interactive menu
        await interactive_menu()


if __name__ == "__main__":
    asyncio.run(main())
