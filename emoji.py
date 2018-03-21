# This Python file uses the following encoding: utf-8
import sys

def score(w1, w2):
    if len(w1) == 0:
        return len(w2)
    if len(w2) == 0:
        return len(w1)
    if w1[-1] == w2[-1]:
        cost = 0
    else:
        cost = 1
    return min(score(w1[:-1], w2) + 1,
               score(w1, w2[:-1]) + 1,
               score(w1[:-1], w2[:-1]) + cost)

if __name__ == "__main__":
    # emojis = ["apple", "lemon", "tomato", "hot_pepper", "corn", "sweet_potato", "cheese_wedge", "meat_on_bone",
    #           "fried_shrimp", "egg", "hamburger", "fries", "hotdog", "pizza", "spaghetti", "taco"]
    emojis = ["apple", "lemon", "tomato", "corn", "egg", "hamburger", "fries", "hotdog", "pizza", "spaghetti", "taco"]
    if len(sys.argv) == 2:
        scores = []
        str = sys.argv[1]
        for word in str.split():
            for emoji in emojis:
                old_score = score(word, emoji)
                new_score = 2.0 * old_score / (len(word) + len(emoji))
                scores.append((word, emoji, old_score, new_score))

        for x in sorted(scores, key=lambda t: t[3]):
            print x
