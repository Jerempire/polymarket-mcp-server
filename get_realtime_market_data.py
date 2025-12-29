#!/usr/bin/env python3
"""
Get Real-Time Prediction Market Data
Shows current prices, probabilities, volume, liquidity, and other market info
"""
import asyncio
import sys
sys.path.insert(0, 'src')

from polymarket_mcp.tools import market_discovery, market_analysis


async def get_realtime_market_data(search_query: str = None):
    """
    Get real-time data for prediction markets

    Args:
        search_query: Search for specific markets (e.g., "Trump", "Bitcoin", "NFL")
                     If None, gets trending markets
    """
    print("=" * 80)
    print("📊 REAL-TIME POLYMARKET DATA")
    print("=" * 80)

    # Step 1: Find markets
    if search_query:
        print(f"\n🔍 Searching for: '{search_query}'...")
        markets = await market_discovery.search_markets(
            query=search_query,
            limit=5,
            filters={"active": "true"}
        )
    else:
        print("\n🔥 Getting trending markets...")
        markets = await market_discovery.get_trending_markets(
            timeframe="24h",
            limit=5
        )

    print(f"✅ Found {len(markets)} markets\n")

    # Step 2: Get detailed data for each market
    for i, market in enumerate(markets, 1):
        market_id = market.get("id") or market.get("market_id")
        question = market.get("question", "Unknown")

        print("=" * 80)
        print(f"📈 MARKET #{i}: {question}")
        print("=" * 80)

        try:
            # Get comprehensive market details
            details = await market_analysis.get_market_details(market_id=market_id)

            # Basic Info
            print("\n📋 BASIC INFO:")
            print(f"  Market ID: {market_id}")
            print(f"  Active: {'✅ Yes' if details.get('active') else '❌ No'}")
            print(f"  Category: {', '.join(details.get('tags', ['N/A']))}")

            # Current Probabilities/Prices
            print("\n💰 CURRENT PROBABILITIES:")
            tokens = details.get("tokens", [])

            if len(tokens) >= 2:
                yes_token = tokens[0]
                no_token = tokens[1]

                try:
                    # Get YES token price
                    yes_price_data = await market_analysis.get_current_price(
                        token_id=yes_token.get("token_id"),
                        side="BOTH"
                    )

                    # Get NO token price
                    no_price_data = await market_analysis.get_current_price(
                        token_id=no_token.get("token_id"),
                        side="BOTH"
                    )

                    # Display prices (prices represent probabilities in decimal)
                    yes_prob = yes_price_data.mid * 100 if yes_price_data.mid else 0
                    no_prob = no_price_data.mid * 100 if no_price_data.mid else 0

                    print(f"  YES: {yes_prob:.1f}% (${yes_price_data.mid:.4f})")
                    print(f"    ├─ Bid: ${yes_price_data.bid:.4f}")
                    print(f"    └─ Ask: ${yes_price_data.ask:.4f}")

                    print(f"  NO:  {no_prob:.1f}% (${no_price_data.mid:.4f})")
                    print(f"    ├─ Bid: ${no_price_data.bid:.4f}")
                    print(f"    └─ Ask: ${no_price_data.ask:.4f}")

                    # Get spread
                    spread_data = await market_analysis.get_spread(
                        token_id=yes_token.get("token_id")
                    )
                    print(f"\n  📊 Spread: {spread_data['spread_percentage']:.2f}%")

                except Exception as price_error:
                    print(f"  ⚠️  Could not fetch live prices: {price_error}")

            # Volume Statistics
            print("\n📊 TRADING VOLUME:")
            volume_data = await market_analysis.get_market_volume(market_id)
            print(f"  24h:  ${volume_data.volume_24h:,.2f}")
            print(f"  7d:   ${volume_data.volume_7d:,.2f}")
            print(f"  30d:  ${volume_data.volume_30d:,.2f}")

            # Liquidity
            liquidity_data = await market_analysis.get_liquidity(market_id)
            liquidity_usd = liquidity_data.get("liquidity_usd", 0)
            print(f"\n💧 LIQUIDITY: ${liquidity_usd:,.2f}")

            # Market closes
            end_date = details.get("endDate") or details.get("end_date_iso")
            if end_date:
                print(f"\n⏰ CLOSES: {end_date}")

            # AI Analysis
            print("\n🤖 AI ANALYSIS:")
            try:
                analysis = await market_analysis.analyze_market_opportunity(market_id)
                print(f"  Recommendation: {analysis.recommendation}")
                print(f"  Confidence: {analysis.confidence_score}%")
                print(f"  Risk Level: {analysis.risk_assessment.upper()}")
                print(f"  Reasoning: {analysis.reasoning}")
            except Exception as analysis_error:
                print(f"  ⚠️  Analysis unavailable: {analysis_error}")

        except Exception as e:
            print(f"  ❌ Error fetching market data: {e}")

        print()

    print("\n" + "=" * 80)
    print("✅ Real-time data fetch complete!")
    print("=" * 80)


async def show_orderbook(token_id: str, depth: int = 10):
    """
    Show detailed orderbook for a specific token

    Args:
        token_id: The token ID to get orderbook for
        depth: Number of price levels to show (default 10)
    """
    print(f"\n📖 ORDERBOOK - Token {token_id}")
    print("=" * 80)

    try:
        orderbook = await market_analysis.get_orderbook(
            token_id=token_id,
            depth=depth
        )

        print("\n💚 BIDS (Buy Orders):")
        print(f"{'Price':>12} {'Size':>12} {'Total':>12}")
        print("-" * 40)
        for bid in orderbook.bids[:depth]:
            total = bid.price * bid.size
            print(f"${bid.price:>11.4f} {bid.size:>12.2f} ${total:>11.2f}")

        print("\n❤️  ASKS (Sell Orders):")
        print(f"{'Price':>12} {'Size':>12} {'Total':>12}")
        print("-" * 40)
        for ask in orderbook.asks[:depth]:
            total = ask.price * ask.size
            print(f"${ask.price:>11.4f} {ask.size:>12.2f} ${total:>11.2f}")

    except Exception as e:
        print(f"❌ Error fetching orderbook: {e}")


async def monitor_category(category: str, limit: int = 5):
    """
    Monitor all markets in a specific category

    Args:
        category: Category name (e.g., "Politics", "Sports", "Crypto")
        limit: Number of markets to show
    """
    print(f"\n📂 MONITORING CATEGORY: {category}")
    print("=" * 80)

    markets = await market_discovery.filter_markets_by_category(
        category=category,
        active_only=True,
        limit=limit
    )

    print(f"Found {len(markets)} active markets in {category}\n")

    for i, market in enumerate(markets, 1):
        question = market.get("question", "Unknown")
        volume_24h = market.get("volume24hr", 0) or 0
        liquidity = market.get("liquidity", 0) or 0

        print(f"{i}. {question[:60]}...")
        print(f"   Volume: ${volume_24h:,.0f} | Liquidity: ${liquidity:,.0f}")


# Example usage
async def main():
    """Main entry point with examples"""

    # Example 1: Get trending markets with real-time data
    print("\n🔥 EXAMPLE 1: Trending Markets with Real-Time Data")
    await get_realtime_market_data()

    # Example 2: Search for specific markets
    print("\n\n🔍 EXAMPLE 2: Search Specific Markets")
    await get_realtime_market_data(search_query="Trump")

    # Example 3: Monitor a category
    print("\n\n📂 EXAMPLE 3: Monitor Category")
    await monitor_category("Politics", limit=3)

    # Example 4: Crypto markets
    print("\n\n💰 EXAMPLE 4: Crypto Markets")
    crypto_markets = await market_discovery.get_crypto_markets(
        symbol="BTC",
        limit=3
    )
    print(f"Found {len(crypto_markets)} Bitcoin markets:")
    for market in crypto_markets:
        print(f"  • {market.get('question', 'Unknown')}")

    # Example 5: Markets closing soon
    print("\n\n⏰ EXAMPLE 5: Markets Closing Soon")
    closing_soon = await market_discovery.get_closing_soon_markets(
        hours=24,
        limit=3
    )
    print(f"Found {len(closing_soon)} markets closing in next 24 hours:")
    for market in closing_soon:
        question = market.get("question", "Unknown")[:60]
        end_date = market.get("endDate") or market.get("end_date_iso", "Unknown")
        print(f"  • {question}... (Closes: {end_date})")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())

    # Or run specific queries:
    # asyncio.run(get_realtime_market_data("Bitcoin"))
    # asyncio.run(monitor_category("Sports"))
