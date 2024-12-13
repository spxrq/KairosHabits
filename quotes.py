from random import choice

class StoicQuotes:
    def __init__(self):
        self.quotes = [
            {
                "text": "Memento mori—remember that you will die.",
                "author": "Marcus Aurelius"
            },
            {
                "text": "You could leave life right now. Let that determine what you do and say and think.",
                "author": "Marcus Aurelius"
            },
            {
                "text": "Let us prepare our minds as if we'd come to the very end of life. Let us postpone nothing.",
                "author": "Seneca"
            },
            {
                "text": "Think of yourself as dead. You have lived your life. Now take what's left and live it properly.",
                "author": "Marcus Aurelius"
            },
            {
                "text": "Time is like a river of passing events, and strong is its current.",
                "author": "Marcus Aurelius"
            },
            {
                "text": "Do not act as if you had ten thousand years to live.",
                "author": "Marcus Aurelius"
            },
            {
                "text": "Life is long if you know how to use it.",
                "author": "Seneca"
            },
            {
                "text": "It is not death that a man should fear, but never beginning to live.",
                "author": "Marcus Aurelius"
            },
            {
                "text": "What we do now echoes in eternity.",
                "author": "Marcus Aurelius"
            },
            {
                "text": "Live each day as if it were your last.",
                "author": "Marcus Aurelius"
            }
        ]
        
    def get_random_quote(self):
        """Returns a random quote from the collection"""
        return choice(self.quotes)