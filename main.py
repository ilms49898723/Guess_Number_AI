#!/usr/bin/env python3


import argparse
import sys


class GuessNumberChecker:
    """
    A guess number game with an answer number.
    """

    def __init__(self, answer_number: str):
        """
        Initialize a new game with an answer number.

        :param answer_number: answer number
        :type answer_number: str
        """
        self._answer_number = answer_number

    @staticmethod
    def is_valid_answer(answer_number: str) -> bool:
        """
        Check whether the answer number is valid.
        That is, no duplicated digits in the number and the length of the number is 4.

        :param answer_number: answer number to check
        :type answer_number: str
        :return: True if valid, False otherwise
        :rtype: bool
        """
        target = answer_number
        if len(target) != 4:
            return False
        if not target.isnumeric():
            return False
        for i in range(3):
            if target[i] in target[i + 1:]:
                return False
        return True

    def answer(self, query: str) -> str:
        """
        Check user's number with the answer number(the correct one).
        Return a string with format aAbB.

        :param query: the number user entered
        :type query: str
        :return: a string with format aAbB to show the result
        :rtype: str
        """
        count_a, count_b = 0, 0
        for i in range(4):
            if query[i] == self._answer_number[i]:
                count_a += 1
            elif query[i] in self._answer_number:
                count_b += 1
        return '{}A{}B'.format(count_a, count_b)


class GuessNumberTree:
    """
    Guess number decision tree module.
    """

    class TreeNode:
        """
        Tree node.
        """

        def __init__(self, record: str = ''):
            """
            Initialize a tree node.

            :param record: node value, number to guess
            :type record: str
            """
            self.record = record
            self.next = [None] * 25

        def initialize(self, record: str = ''):
            """
            Initialize a tree node.

            :param record: node value, number to guess
            :type record: str
            :return: None
            :rtype: None
            """
            self.record = record
            self.next = [None] * 25

    def __init__(self):
        """
        Initialize a tree.
        """
        self.root = None
        self.initialize()

    def initialize(self):
        """
        Initialize a tree.

        :return: None
        :rtype: None
        """
        self.root = GuessNumberTree.TreeNode('0123')


class GuessNumberAI:
    """
    Guess Number AI.
    """

    def __init__(self):
        """
        Initialize a new Guess Number AI object.
        """
        self._previous = ''
        self._log = []
        self._records = set()
        self._numbers = {'{:04d}'.format(i) for i in range(10000) if GuessNumberAI.is_valid_answer('{:04d}'.format(i))}
        self._number_list = list(sorted(self._numbers))
        self._tree = GuessNumberTree()
        self.initialize()

    def initialize(self):
        """
        Initialize all records, data.

        :return: None
        :rtype: None
        """
        self._previous = ''
        self._log = []
        self._records = self._numbers.copy()

    def _check_result(self, number: str, a: int, b: int) -> bool:
        """
        Compare the number to the previous guessed number with condition aAbB.

        :param number: number to check
        :type number: str
        :param a: numbers of the numbers in correct position
        :type a: int
        :param b: number of the numbers in wrong position
        :type b: int
        :return: True if the condition is satisfied, False otherwise
        :rtype: bool
        """
        count_a, count_b = 0, 0
        for i in range(4):
            if number[i] == self._previous[i]:
                count_a += 1
            elif number[i] in self._previous:
                count_b += 1
        return count_a == a and count_b == b

    def _filter_record(self, a: int, b: int):
        """
        Delete all numbers in records that don't satisfied the condition aAbB of previous guess.

        :param a: numbers of the numbers in correct position
        :type a: int
        :param b: number of the numbers in wrong position
        :type b: int
        :return: None
        :rtype: None
        """
        to_delete = [key for key in self._records if not self._check_result(key, a, b)]
        for key in to_delete:
            self._records.remove(key)

    def _calculate_score(self, number: str) -> int:
        """
        Calculate the score of the number using max(n1, n2, n3, ..., nm).

        :param number: number to calculate
        :type number: str
        :return: score of the number
        :rtype: int
        """
        result = [0] * 25
        for key in self._records:
            count_a, count_b = 0, 0
            for i in range(4):
                if number[i] == key[i]:
                    count_a += 1
                elif number[i] in key:
                    count_b += 1
            result[count_a * 5 + count_b] += 1
        return max(*result)

    def _search_tree(self, a: int, b: int) -> str:
        """
        Search decision tree to try to find next number to guess.

        :param a: numbers of the numbers in correct position
        :type a: int
        :param b: number of the numbers in wrong position
        :type b: int
        :return: next guess number, '' if not found in tree
        :rtype: str
        """
        tree_node = self._tree.root
        for key in self._log:
            if tree_node.next[key[0] * 5 + key[1]] is not None:
                tree_node = tree_node.next[key[0] * 5 + key[1]]
        if tree_node.next[a * 5 + b] is None:
            return ''
        else:
            return tree_node.next[a * 5 + b].record

    def _update_tree(self, next_guess: str, a: int, b: int):
        """
        Update decision tree with number selected from minimum score calculated.

        :param next_guess: next number to guess
        :type next_guess: str
        :param a: numbers of the numbers in correct position
        :type a: int
        :param b: number of the numbers in wrong position
        :type b: int
        :return: None
        :rtype: None
        """
        tree_node = self._tree.root
        for key in self._log:
            if tree_node.next[key[0] * 5 + key[1]] is not None:
                tree_node = tree_node.next[key[0] * 5 + key[1]]
        if tree_node.next[a * 5 + b] is None:
            tree_node.next[a * 5 + b] = GuessNumberTree.TreeNode(next_guess)

    def guess(self, result: str) -> str:
        """
        Get the next guess number.
        The next number is chosen by min(all scores of the numbers).

        :param result: the result string of the precious guess, None if it's the first time
        :type result: str
        :return: the number to guess next
        :rtype: str
        """
        if result is None:
            self.initialize()
            self._previous = '0123'
            return self._previous
        a, b = int(result[0]), int(result[2])
        self._filter_record(a, b)
        if len(self._records) == 1:
            return next(iter(self._records))
        search_result = self._search_tree(a, b)
        if search_result != '':
            self._previous = search_result
        else:
            candidate = ('', 1e5)
            for key in self._number_list:
                key_score = self._calculate_score(key)
                if key_score < candidate[1]:
                    candidate = (key, key_score)
            self._update_tree(candidate[0], a, b)
            self._previous = candidate[0]
        self._log.append((a, b))
        return self._previous

    @staticmethod
    def is_valid_answer(answer_number: str) -> bool:
        """
        Check whether the answer number is valid.
        That is, no duplicated digits in the number and the length of it is 4.

        :param answer_number: answer number to check
        :type answer_number: str
        :return: True if valid, False otherwise
        :rtype: bool
        """
        target = answer_number
        if len(target) != 4:
            return False
        if not target.isnumeric():
            return False
        for i in range(3):
            if target[i] in target[i + 1:]:
                return False
        return True


class GuessNumberAISelfTest:
    """
    Guess Number AI Self Test.
    """

    @staticmethod
    def _play(answer_number: str, guess_number_ai: GuessNumberAI) -> int:
        """
        Run a game with the answer given.

        :param answer_number: the answer number
        :type answer_number: str
        :param guess_number_ai: guess number ai
        :type guess_number_ai: GuessNumberAI
        :return: times tried, counted from 1
        :rtype: int
        """
        game_checker = GuessNumberChecker(answer_number)
        guess_number_ai.initialize()
        logs = []
        result = None
        tried = 0
        while result != '4A0B':
            tried += 1
            guess = guess_number_ai.guess(result)
            result = game_checker.answer(guess)
            logs.append('Round-{} {} {}'.format(tried, guess, result))
            if tried >= 10:
                print('[!] Answer number', answer_number, 'has already tried 10 times. Terminated!')
                break
        if tried > 7:
            for key in logs:
                print(key)
        return tried

    @staticmethod
    def start_self_test(start: int = 0, end: int = 10000, guess_number_ai: GuessNumberAI = None) -> int:
        """
        Start a full test with all possible answer numbers in [start, end).

        :param start: lower bound of answer numbers
        :type start: int
        :param end: upper bound of answer numbers(exclusive)
        :type end: int
        :param guess_number_ai: guess number ai, None-able
        :type guess_number_ai: GuessNumberAI
        :return: maximum times tried
        :rtype: int
        """
        if guess_number_ai is None:
            guess_number_ai = GuessNumberAI()
        numbers = ['{:04d}'.format(i) for i in range(start, end) if GuessNumberAI.is_valid_answer('{:04d}'.format(i))]
        print('Size of test data', len(numbers), 'in range [', start, ',', end, ')')
        max_value = 0
        for number in numbers:
            tried = GuessNumberAISelfTest._play(number, guess_number_ai)
            max_value = max(max_value, tried)
            if tried > 7:
                print('Number', number, 'tried', tried, 'times')
        print('Maximum times used:', max_value, 'times', end='\n\n')
        return max_value


def self_test():
    """
    Run all tests.

    :return: None
    :rtype: None
    """
    guess_number_ai = GuessNumberAI()
    for i in range(10):
        print('Run tests from', i * 1000, 'to', (i + 1) * 1000)
        GuessNumberAISelfTest.start_self_test(start=i * 1000, end=(i + 1) * 1000, guess_number_ai=guess_number_ai)


def play(answer_number: str, guess_number_ai: GuessNumberAI) -> int:
    """
    Start a new game.
    With output string according to homework specs.

    :param answer_number: answer number
    :type answer_number: str
    :param guess_number_ai: guess number ai
    :type guess_number_ai: GuessNumberAI
    :return: times tried
    :rtype: int
    """
    game_checker = GuessNumberChecker(answer_number)
    guess_number_ai.initialize()
    result = None
    tried = 0
    while result != '4A0B':
        tried += 1
        guess = guess_number_ai.guess(result)
        result = game_checker.answer(guess)
        print('Round-{} {} {}'.format(tried, guess, result))
    return tried


def main():
    """
    Main function.

    :return: None
    :rtype: None
    """
    parser = argparse.ArgumentParser(description='Guess Number AI')
    parser.add_argument('answer_numbers', type=str, nargs='*', help='answer numbers')
    args = parser.parse_args()
    guess_number_ai = GuessNumberAI()
    if len(args.answer_numbers) == 0:
        while True:
            try:
                answer_number = str(input())
                if not GuessNumberChecker.is_valid_answer(answer_number):
                    print('Invalid answer number', answer_number)
                    continue
                play(answer_number, guess_number_ai)
            except EOFError:
                break
    else:
        answer_numbers = args.answer_numbers
        for answer_number in answer_numbers:
            if not GuessNumberChecker.is_valid_answer(answer_number):
                print('Invalid answer number', answer_number)
                sys.exit(1)
        for answer_number in answer_numbers:
            play(answer_number, guess_number_ai)
            print()


if __name__ == '__main__':
    main()
    # self_test()
