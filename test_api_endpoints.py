"""
JAKE API Endpoint Test Script

Tests all API endpoints to ensure the system is working correctly.
Run this after starting the server with: python -m src.main
"""

import requests
import json
import time
from typing import Dict, Any
import sys


class Colors:
    """Terminal colors for pretty output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class JAKEAPITester:
    """Test suite for JAKE API endpoints"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.character_id = None
        self.session_id = None
        self.quest_id = None

    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{text:^70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

    def print_test(self, test_name: str):
        """Print test name"""
        print(f"{Colors.BOLD}{Colors.BLUE}🧪 Testing: {test_name}{Colors.RESET}")

    def print_success(self, message: str):
        """Print success message"""
        print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

    def print_error(self, message: str):
        """Print error message"""
        print(f"{Colors.RED}✗ {message}{Colors.RESET}")

    def print_info(self, message: str):
        """Print info message"""
        print(f"{Colors.YELLOW}ℹ {message}{Colors.RESET}")

    def print_data(self, label: str, data: Any):
        """Print data in a formatted way"""
        print(f"{Colors.MAGENTA}  {label}: {Colors.RESET}{data}")

    def record_result(self, test_name: str, passed: bool, details: str = ""):
        """Record test result"""
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })

    def test_health_check(self) -> bool:
        """Test: GET /ping - Health check endpoint"""
        self.print_test("Health Check (GET /ping)")

        try:
            response = requests.get(f"{self.base_url}/ping", timeout=5)

            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Server is healthy: {data}")
                self.record_result("Health Check", True)
                return True
            else:
                self.print_error(f"Health check failed with status {response.status_code}")
                self.record_result("Health Check", False, f"Status: {response.status_code}")
                return False

        except requests.exceptions.ConnectionError:
            self.print_error("Cannot connect to server. Is it running?")
            self.print_info("Start the server with: python -m src.main")
            self.record_result("Health Check", False, "Connection refused")
            return False
        except Exception as e:
            self.print_error(f"Error: {str(e)}")
            self.record_result("Health Check", False, str(e))
            return False

    def test_create_character(self) -> bool:
        """Test: POST /characters - Create a new character"""
        self.print_test("Create Character (POST /characters)")

        character_data = {
            "user_id": "test_user_001",
            "name": "Luna",
            "age": "25",
            "occupation": "Cafe owner",
            "additional_info": "Loves books, coffee, and rainy days. Very friendly and warm."
        }

        try:
            response = requests.post(
                f"{self.base_url}/characters",
                json=character_data,
                timeout=60  # Character creation can take time
            )

            if response.status_code == 200:
                data = response.json()
                self.character_id = data.get("character_id")

                self.print_success(f"Character created successfully!")
                self.print_data("Character ID", self.character_id)
                self.print_data("Name", data.get("name"))
                self.print_data("Worldview (excerpt)", data.get("worldview", "")[:100] + "...")
                self.print_data("Personality (excerpt)",
                              data.get("details", {}).get("personality", "")[:80] + "...")

                self.record_result("Create Character", True)
                return True
            else:
                self.print_error(f"Failed with status {response.status_code}")
                self.print_data("Response", response.text)
                self.record_result("Create Character", False, f"Status: {response.status_code}")
                return False

        except Exception as e:
            self.print_error(f"Error: {str(e)}")
            self.record_result("Create Character", False, str(e))
            return False

    def test_get_character(self) -> bool:
        """Test: GET /characters/{id} - Get character details"""
        self.print_test(f"Get Character (GET /characters/{self.character_id})")

        if not self.character_id:
            self.print_error("No character ID available. Skipping.")
            self.record_result("Get Character", False, "No character ID")
            return False

        try:
            response = requests.get(f"{self.base_url}/characters/{self.character_id}")

            if response.status_code == 200:
                data = response.json()

                self.print_success("Character retrieved successfully!")
                self.print_data("Character ID", data.get("character_id"))
                self.print_data("Name", data.get("name"))
                self.print_data("Age", data.get("age"))
                self.print_data("Occupation", data.get("occupation"))

                self.record_result("Get Character", True)
                return True
            else:
                self.print_error(f"Failed with status {response.status_code}")
                self.record_result("Get Character", False, f"Status: {response.status_code}")
                return False

        except Exception as e:
            self.print_error(f"Error: {str(e)}")
            self.record_result("Get Character", False, str(e))
            return False

    def test_chat_first_message(self) -> bool:
        """Test: POST /characters/{id}/chat - First chat message"""
        self.print_test(f"First Chat Message (POST /characters/{self.character_id}/chat)")

        if not self.character_id:
            self.print_error("No character ID available. Skipping.")
            self.record_result("First Chat", False, "No character ID")
            return False

        try:
            response = requests.post(
                f"{self.base_url}/characters/{self.character_id}/chat",
                json={"message": "Hello! This cafe looks really cozy."},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("session_id")

                self.print_success("Chat response received!")
                self.print_data("Session ID", self.session_id)
                self.print_data("Dialogue", data.get("dialogue"))
                self.print_data("Action", data.get("action"))
                self.print_data("Affection Score", data.get("affection_score"))
                self.print_data("Affection Change", data.get("affection_change"))
                self.print_data("Turn Count", data.get("turn_count"))
                self.print_data("Memories Extracted", data.get("memories_extracted"))

                self.record_result("First Chat", True)
                return True
            else:
                self.print_error(f"Failed with status {response.status_code}")
                self.print_data("Response", response.text)
                self.record_result("First Chat", False, f"Status: {response.status_code}")
                return False

        except Exception as e:
            self.print_error(f"Error: {str(e)}")
            self.record_result("First Chat", False, str(e))
            return False

    def test_chat_with_session(self) -> bool:
        """Test: POST /characters/{id}/chat - Chat with existing session"""
        self.print_test("Chat with Session (with X-Session-Id header)")

        if not self.character_id or not self.session_id:
            self.print_error("No character/session ID available. Skipping.")
            self.record_result("Chat with Session", False, "No IDs")
            return False

        messages = [
            "What kind of books do you like?",
            "That sounds interesting! Do you have any recommendations?",
            "I'd love to visit your cafe more often!"
        ]

        try:
            for i, message in enumerate(messages, 2):
                self.print_info(f"Message {i}: {message}")

                response = requests.post(
                    f"{self.base_url}/characters/{self.character_id}/chat",
                    json={"message": message},
                    headers={"X-Session-Id": self.session_id},
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    self.print_success(f"Turn {data.get('turn_count')}")
                    self.print_data("  Luna says", data.get("dialogue")[:100] + "...")
                    self.print_data("  Affection", f"{data.get('affection_score')} ({data.get('affection_change'):+d})")
                else:
                    self.print_error(f"Failed with status {response.status_code}")
                    self.record_result("Chat with Session", False, f"Message {i} failed")
                    return False

                time.sleep(0.5)  # Brief pause between messages

            self.record_result("Chat with Session", True)
            return True

        except Exception as e:
            self.print_error(f"Error: {str(e)}")
            self.record_result("Chat with Session", False, str(e))
            return False

    def test_create_quest(self) -> bool:
        """Test: POST /characters/{id}/quests - Create a quest"""
        self.print_test(f"Create Quest (POST /characters/{self.character_id}/quests)")

        if not self.character_id:
            self.print_error("No character ID available. Skipping.")
            self.record_result("Create Quest", False, "No character ID")
            return False

        quest_data = {
            "quest_type": "regular",
            "title": "Getting to Know Each Other",
            "description": "Ask about Luna's favorite book genre",
            "required_affection": 0
        }

        try:
            response = requests.post(
                f"{self.base_url}/characters/{self.character_id}/quests",
                json=quest_data
            )

            if response.status_code == 200:
                data = response.json()
                self.quest_id = data.get("quest_id")

                self.print_success("Quest created successfully!")
                self.print_data("Quest ID", self.quest_id)
                self.print_data("Title", data.get("title"))
                self.print_data("Type", data.get("quest_type"))
                self.print_data("Cleared", data.get("cleared"))

                self.record_result("Create Quest", True)
                return True
            else:
                self.print_error(f"Failed with status {response.status_code}")
                self.record_result("Create Quest", False, f"Status: {response.status_code}")
                return False

        except Exception as e:
            self.print_error(f"Error: {str(e)}")
            self.record_result("Create Quest", False, str(e))
            return False

    def test_list_quests(self) -> bool:
        """Test: GET /characters/{id}/quests - List character quests"""
        self.print_test(f"List Quests (GET /characters/{self.character_id}/quests)")

        if not self.character_id:
            self.print_error("No character ID available. Skipping.")
            self.record_result("List Quests", False, "No character ID")
            return False

        try:
            response = requests.get(f"{self.base_url}/characters/{self.character_id}/quests")

            if response.status_code == 200:
                data = response.json()

                self.print_success("Quests retrieved successfully!")
                self.print_data("Character ID", data.get("character_id"))
                self.print_data("Regular Quests", len(data.get("regular_quests", [])))
                self.print_data("Advancement Quests", len(data.get("advancement_quests", [])))

                for quest in data.get("regular_quests", []):
                    status = "✓ Cleared" if quest.get("cleared") == 1 else "○ Not cleared"
                    self.print_info(f"  {status} - {quest.get('title')}")

                self.record_result("List Quests", True)
                return True
            else:
                self.print_error(f"Failed with status {response.status_code}")
                self.record_result("List Quests", False, f"Status: {response.status_code}")
                return False

        except Exception as e:
            self.print_error(f"Error: {str(e)}")
            self.record_result("List Quests", False, str(e))
            return False

    def test_conversation_history(self) -> bool:
        """Test: GET /conversations/{session_id} - Get conversation history"""
        self.print_test(f"Conversation History (GET /conversations/{self.session_id})")

        if not self.session_id:
            self.print_error("No session ID available. Skipping.")
            self.record_result("Conversation History", False, "No session ID")
            return False

        try:
            response = requests.get(f"{self.base_url}/conversations/{self.session_id}")

            if response.status_code == 200:
                data = response.json()

                self.print_success("Conversation history retrieved!")
                self.print_data("Session ID", data.get("session_id"))
                self.print_data("Character ID", data.get("character_id"))
                self.print_data("Affection Score", data.get("affection_score"))
                self.print_data("Relationship Stage", data.get("relationship_stage"))
                self.print_data("Turn Count", data.get("turn_count"))
                self.print_data("Total Messages", len(data.get("messages", [])))

                self.record_result("Conversation History", True)
                return True
            else:
                self.print_error(f"Failed with status {response.status_code}")
                self.record_result("Conversation History", False, f"Status: {response.status_code}")
                return False

        except Exception as e:
            self.print_error(f"Error: {str(e)}")
            self.record_result("Conversation History", False, str(e))
            return False

    def test_search_memories(self) -> bool:
        """Test: GET /characters/{id}/memories - Search character memories"""
        self.print_test(f"Search Memories (GET /characters/{self.character_id}/memories)")

        if not self.character_id:
            self.print_error("No character ID available. Skipping.")
            self.record_result("Search Memories", False, "No character ID")
            return False

        try:
            response = requests.get(
                f"{self.base_url}/characters/{self.character_id}/memories",
                params={"query": "books and reading", "limit": 5}
            )

            if response.status_code == 200:
                data = response.json()

                self.print_success("Memory search completed!")
                self.print_data("Query", data.get("query"))
                self.print_data("Results", len(data.get("memories", [])))

                for i, memory in enumerate(data.get("memories", [])[:3], 1):
                    self.print_info(f"  {i}. {memory.get('content')}")

                self.record_result("Search Memories", True)
                return True
            else:
                self.print_error(f"Failed with status {response.status_code}")
                self.record_result("Search Memories", False, f"Status: {response.status_code}")
                return False

        except Exception as e:
            self.print_error(f"Error: {str(e)}")
            self.record_result("Search Memories", False, str(e))
            return False

    def test_list_user_characters(self) -> bool:
        """Test: GET /users/{user_id}/characters - List user's characters"""
        self.print_test("List User Characters (GET /users/test_user_001/characters)")

        try:
            response = requests.get(f"{self.base_url}/users/test_user_001/characters")

            if response.status_code == 200:
                data = response.json()

                self.print_success("User characters retrieved!")
                self.print_data("User ID", data.get("user_id"))
                self.print_data("Total Characters", len(data.get("characters", [])))

                for char in data.get("characters", []):
                    self.print_info(f"  - {char.get('name')} ({char.get('occupation')})")

                self.record_result("List User Characters", True)
                return True
            else:
                self.print_error(f"Failed with status {response.status_code}")
                self.record_result("List User Characters", False, f"Status: {response.status_code}")
                return False

        except Exception as e:
            self.print_error(f"Error: {str(e)}")
            self.record_result("List User Characters", False, str(e))
            return False

    def run_all_tests(self):
        """Run all API tests"""
        self.print_header("JAKE API ENDPOINT TESTS")

        print(f"{Colors.BOLD}Testing API at: {self.base_url}{Colors.RESET}\n")

        # Test 1: Health Check
        if not self.test_health_check():
            self.print_error("\n❌ Server is not running. Please start it first:")
            self.print_info("   python -m src.main")
            return

        time.sleep(0.5)

        # Test 2: Create Character
        self.test_create_character()
        time.sleep(1)

        # Test 3: Get Character
        self.test_get_character()
        time.sleep(0.5)

        # Test 4: First Chat
        self.test_chat_first_message()
        time.sleep(1)

        # Test 5: Chat with Session
        self.test_chat_with_session()
        time.sleep(0.5)

        # Test 6: Create Quest
        self.test_create_quest()
        time.sleep(0.5)

        # Test 7: List Quests
        self.test_list_quests()
        time.sleep(0.5)

        # Test 8: Conversation History
        self.test_conversation_history()
        time.sleep(0.5)

        # Test 9: Search Memories
        self.test_search_memories()
        time.sleep(0.5)

        # Test 10: List User Characters
        self.test_list_user_characters()

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")

        passed = sum(1 for r in self.test_results if r["passed"])
        total = len(self.test_results)
        failed = total - passed

        print(f"{Colors.BOLD}Total Tests: {total}{Colors.RESET}")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")
        print(f"Success Rate: {(passed/total*100):.1f}%\n")

        if failed > 0:
            print(f"{Colors.BOLD}{Colors.RED}Failed Tests:{Colors.RESET}")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"{Colors.RED}  ✗ {result['test']}: {result['details']}{Colors.RESET}")

        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")

        if failed == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! JAKE API is working perfectly!{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  Some tests failed. Check the details above.{Colors.RESET}")

        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Test JAKE API endpoints")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="API base URL (default: http://localhost:8000)"
    )

    args = parser.parse_args()

    tester = JAKEAPITester(base_url=args.url)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
