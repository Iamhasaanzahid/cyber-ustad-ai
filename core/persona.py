# ------------------------------ #
#  persona.py
#  =============================
#  *  Yeh file ek simple "Persona" object define karti hai
#  *  Jo aapke chatbot ko *Jigri Dost* vibe deta hai: 
#         *  Hinglish mix (Roman Urdu + English)
#         *  Light‑hearted sarcasm (harami jokes)
#         *  Cyber‑security examples added on demand
#  *  Isko aap apne main bot script mein import karke
#     `chat_with_ustad()` function ko call kar sakte hain.
#  *  Demo usage neeche diya gaya hai.
# ------------------------------ #

from dataclasses import dataclass, field
import random

@dataclass
class CyberUstadPersona:
    """Simple persona definition – just enough to mimic the “CyberUstad” vibe."""

    # Basic identifiers
    name: str = "CyberUstad"
    language: str = "urdish_hinglish"

    # Pre‑defined roast/joke patterns (short & punchy)
    roasts: list[str] = field(default_factory=lambda: [
        "Bhai, tu Nmap ko khana samajh liya? 😅",
        "Tera firewall load‑shedding se zyada down hai! 🔥",
        "Phone ki battery se bhi jaldi tera session expire hota hai! 💔",
        "Tu itna confident, lekin syllabus parhi? CEH ka degree abhi tak! 😉"
    ])

    # Small cyber‑security examples – each key is a topic,
    # value is a short narrative + a quick command/example
    examples: dict[str, str] = field(default_factory=lambda: {
        "nmap_scan": (
            "Imagine tu ek CCTV camera laga raha hai, lekin tu sirf ek photo le raha hai.\n"
            "Isko Nmap ke through karna: `nmap -sV 192.168.1.1-254`\n"
            "Ab picture se pata chal jayega ki kaun sa device, kaunsa port open…"
        ),
        "sql_injection": (
            "SQLi ek dum dukaandar ko 'tijori khol dena' bolne jaisa hai.\n"
            "Login form mein daal: `admin' OR '1'='1 --`\n"
            "Aur result: `SELECT * FROM users WHERE username='admin' OR '1'='1' --`"
        ),
        "phishing": (
            "Phishing ko ek fake bakery samajh. \n"
            "Jab wo ‘chocolate cake’ offer kare, toh dekhna: URL check karo, \n"
            "aur email header mein 'From:' field check karo – agar weird ho toh safe!"
        )
    })

    # Method to fetch a random roast
    def get_roast(self) -> str:
        return random.choice(self.roasts)

    # Method to fetch a cyber example by topic key
    def get_example(self, topic: str) -> str:
        return self.examples.get(topic,
                                 "Bhai, yeh topic thoda mushkil lag raha hai – koi aur try kar?")

    # Main response builder – mixes roast + example
    def build_response(self, topic: str) -> str:
        roast = self.get_roast()
        example = self.get_example(topic)
        return f"{roast}\n\n{example}\n\nPractice ka sawal: Agar tu '{topic}' ko automate karna chahta hai, "
        # ask user a quick practical question
        if topic == "nmap_scan":
            return roast + "\n\nExample: `nmap -p 80-443 192.168.1.0/24`\n\nPractice ka sawal: Kya tu -sV option use karke service version bhi check karega?"
        if topic == "sql_injection":
            return roast + "\n\nExample: `SELECT * FROM users WHERE username = 'admin' OR '1'='1' --'\n\nPractice ka sawal: Kaise tu query ko sanitize kar sakta hai?"
        if topic == "phishing":
            return roast + "\n\nExample: Email header analysis, URL sanitization\n\nPractice ka sawal: Phishing email ko identify karne ke liye kaunse header fields check karni chahiye?"
        # default
        return roast + "\n\nExample: " + example + "\n\nPractice ka sawal: Kya tu is concept ko real life mein test kar sakta hai?"

# ------------------------------ #
#  Demo usage – ye block tab run hoga
#  jab file directly execute ki jaye (python persona.py)
# ------------------------------ #
if __name__ == "__main__":
    ustad = CyberUstadPersona()
    # User chooses a topic
    topic = input("Kaun sa cyber topic discuss karna hai? (nmap_scan/sql_injection/phishing) : ")
    print("\n" + ustad.build_response(topic.strip()))
