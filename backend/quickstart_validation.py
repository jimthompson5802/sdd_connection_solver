#!/usr/bin/env python3
"""
Quickstart Validation Script

This script validates the main user workflow scenarios from the quickstart guide
by executing the key API calls that would happen in a real user session.
"""

import requests
import json
import tempfile
import os
from pathlib import Path


def create_test_puzzle_file():
    """Create a temporary puzzle file with 16 words."""
    words = [
        "BASS",
        "PIANO",
        "GUITAR",
        "DRUMS",
        "SALMON",
        "TUNA",
        "COD",
        "TROUT",
        "YELLOW",
        "BLUE",
        "RED",
        "GREEN",
        "APPLE",
        "ORANGE",
        "BANANA",
        "GRAPE",
    ]

    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    temp_file.write(",".join(words))
    temp_file.close()

    return temp_file.name


def test_quickstart_scenarios(base_url="http://localhost:8000"):
    """
    Test the main quickstart scenarios:
    1. Upload puzzle file
    2. Create session
    3. Get session state
    4. Check health endpoints
    """

    print("🧩 NYT Connections Puzzle Assistant - Quickstart Validation")
    print("=" * 65)

    results = {
        "puzzle_upload": False,
        "session_creation": False,
        "session_state": False,
        "health_check": False,
        "overall_success": False,
    }

    try:
        # Test 1: Health Check
        print("\n📊 Testing Health Endpoints...")
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server health check passed")
                results["health_check"] = True
            else:
                print(f"❌ Health check failed: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server. Make sure the server is running on localhost:8000")
            return results
        except Exception as e:
            print(f"❌ Health check error: {e}")

        # Test 2: Upload Puzzle File
        print("\n📁 Testing Puzzle Upload...")
        puzzle_file = create_test_puzzle_file()

        try:
            with open(puzzle_file, "rb") as f:
                files = {"file": f}
                data = {"user_id": "quickstart-test-user"}
                response = requests.post(f"{base_url}/api/v1/puzzles/upload", files=files, data=data)  # , timeout=10)

            if response.status_code == 201:
                puzzle_data = response.json()
                puzzle_id = puzzle_data["id"]
                print(f"✅ Puzzle uploaded successfully!")
                print(f"   Puzzle ID: {puzzle_id}")
                print(f"   Words count: {len(puzzle_data['words'])}")
                results["puzzle_upload"] = True

                # Test 3: Create Session
                print("\n🎮 Testing Session Creation...")
                session_data = {"puzzle_id": puzzle_id, "llm_model": "gpt-4", "user_id": "quickstart-test-user"}

                response = requests.post(
                    f"{base_url}/api/v1/sessions",
                    json=session_data,
                    # timeout=10,
                    # headers={"Content-Type": "application/json"},
                )

                if response.status_code == 201:
                    session_info = response.json()
                    session_id = session_info["id"]
                    print(f"✅ Session created successfully!")
                    print(f"   Session ID: {session_id}")
                    print(f"   Status: {session_info['status']}")
                    print(f"   Remaining words: {len(session_info['remaining_words'])}")
                    results["session_creation"] = True

                    # Test 4: Get Session State
                    print("\n📊 Testing Session State Retrieval...")
                    response = requests.get(f"{base_url}/api/v1/sessions/{session_id}", timeout=5)

                    if response.status_code == 200:
                        session_state = response.json()
                        print(f"✅ Session state retrieved successfully!")
                        print(f"   Status: {session_state['status']}")
                        print(f"   Solved groups: {session_state['solved_groups_count']}")
                        print(f"   Can request recommendation: {session_state['can_request_recommendation']}")
                        results["session_state"] = True

                        # Test 5: Attempt to get recommendation (this might fail without LLM setup)
                        print("\n🤖 Testing AI Recommendation Request...")
                        try:
                            response = requests.post(
                                f"{base_url}/api/v1/sessions/{session_id}/recommendations", timeout=30
                            )

                            if response.status_code == 201:
                                recommendation = response.json()
                                print(f"✅ AI recommendation generated!")
                                print(f"   Recommended words: {recommendation['recommended_words']}")
                                print(f"   Explanation: {recommendation['explanation'][:100]}...")
                                print(f"   Processing time: {recommendation['processing_time_ms']}ms")
                            elif response.status_code == 503:
                                print("⚠️  AI service not available (LLM not configured)")
                            else:
                                print(f"⚠️  Recommendation request returned: {response.status_code}")

                        except requests.exceptions.Timeout:
                            print("⚠️  AI recommendation timed out (expected without LLM setup)")
                        except Exception as e:
                            print(f"⚠️  AI recommendation error: {e}")

                    else:
                        print(f"❌ Failed to get session state: {response.status_code}")
                else:
                    print(f"❌ Failed to create session: {response.status_code}")
                    if response.status_code == 400:
                        error_data = response.json()
                        print(f"   Error: {error_data.get('message', 'Unknown error')}")
            else:
                print(f"❌ Failed to upload puzzle: {response.status_code}")
                error_data = response.json()
                print(f"   Error: {error_data.get('message', 'Unknown error')}")

        finally:
            # Clean up temporary file
            os.unlink(puzzle_file)

    except Exception as e:
        print(f"❌ Unexpected error during testing: {e}")

    # Summary
    print("\n" + "=" * 65)
    print("📋 VALIDATION SUMMARY")
    print("=" * 65)

    passed_tests = sum(results.values())
    total_core_tests = 4  # health, upload, session_creation, session_state

    for test_name, passed in results.items():
        if test_name != "overall_success":
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")

    success_rate = (passed_tests / total_core_tests) * 100
    results["overall_success"] = success_rate >= 75

    print(f"\nSuccess Rate: {success_rate:.1f}% ({passed_tests}/{total_core_tests} core tests passed)")

    if results["overall_success"]:
        print("🎉 Quickstart validation SUCCESSFUL!")
        print("   The main user workflow is working correctly.")
    else:
        print("⚠️  Quickstart validation PARTIAL SUCCESS")
        print("   Some core functionality may need attention.")

    return results


if __name__ == "__main__":
    import sys

    # Check if server URL is provided
    server_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

    print(f"Testing server at: {server_url}")
    results = test_quickstart_scenarios(server_url)

    # Exit with appropriate code
    sys.exit(0 if results["overall_success"] else 1)
