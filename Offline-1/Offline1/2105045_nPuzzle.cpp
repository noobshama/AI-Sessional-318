#include <bits/stdc++.h>
#include <chrono>
using namespace std;
using namespace std::chrono;

#define UP 1
#define LEFT 2
#define RIGHT 3
#define DOWN 4

using Board = vector<vector<string>>;

class Node

{

public:
    Board board;

    shared_ptr<Node> previous_state;

    int previous_move;

    int fn;

    int gn;

    int hn;

    Node(Board board1, int direction = 0, shared_ptr<Node> prev = nullptr, int actual_cost = 0, int estimate_total_cost = 0, int heuristic = 0)
    {
        board = board1;

        previous_state = prev;

        previous_move = direction;

        fn = estimate_total_cost;

        gn = actual_cost;

        hn = heuristic;
    }
};

class BoardStructure

{

public:
    static void printBoardElements(Board board)

    {

        for (int i = 0; i < board.size(); i++)

        {

            for (int j = 0; j < board[i].size(); j++)

            {

                cout << board[i][j] << " ";
            }

            cout << endl;
        }

        cout << endl;
    }

    static string same_board(Board board)
    {

        string path = "";

        for (int i = 0; i < board.size(); i++)

        {

            for (int j = 0; j < board[i].size(); j++)

            {

                path += board[i][j] + " ";
            }
        }

        return path;
    }

    static pair<int, int> findBlank(Board board)

    {

        for (int i = 0; i < board.size(); i++)

        {

            for (int j = 0; j < board[i].size(); j++)

            {

                if (board[i][j] == "0")

                {

                    return {i, j};
                }
            }
        }

        return {-1, -1};
    }

    static Board moveDirection(Board board, int direction, int row, int column)

    {

        Board board1 = board;

        switch (direction)

        {

        case UP:

            if (row > 0)

            {

                swap(board1[row][column], board1[row - 1][column]);
            }

            break;

        case LEFT:

            if (column > 0)

            {

                swap(board1[row][column], board1[row][column - 1]);
            }

            break;

        case RIGHT:

            if (column < board.size() - 1)

            {

                swap(board1[row][column], board1[row][column + 1]);
            }

            break;

        case DOWN:

            if (row < board.size() - 1)

            {

                swap(board1[row][column], board1[row + 1][column]);
            }

            break;
        }

        return board1;
    }
};

class SolvablePuzzle
{

public:
    static int conqure(vector<int> &arr, int left, int mid, int right)

    {
        vector<int> arr1;

        int i = left;

        int j = mid + 1;

        int inversions_count = 0;

        while (i <= mid && j <= right)

        {

            if (arr[i] <= arr[j])

            {

                arr1.push_back(arr[i++]);
            }

            else

            {
                arr1.push_back(arr[j++]);

                inversions_count += mid - i + 1;
            }
        }

        while (i <= mid)

        {

            arr1.push_back(arr[i++]);
        }

        while (j <= right)

        {

            arr1.push_back(arr[j++]);
        }
        for (int i = 0; i < arr1.size(); i++)

        {

            arr[left + i] = arr1[i];
        }

        return inversions_count;
    }

    static int divide(vector<int> &arr, int left, int right)

    {

        if (left >= right)

        {

            return 0;
        }

        int mid = (left + right) / 2;

        int inversions_count = divide(arr, left, mid) + divide(arr, mid + 1, right) + conqure(arr, left, mid, right);

        return inversions_count;
    }

    static int countInversions(Board board)

    {

        vector<int> arr;

        for (int i = 0; i < board.size(); i++)

        {
            for (int j = 0; j < board[i].size(); j++)

            {

                if (board[i][j] != "0")

                {

                    arr.push_back(stoi(board[i][j]));
                }
            }
        }

        return divide(arr, 0, arr.size() - 1);
    }

    static bool isSolvable(Board board, int k)

    {
        int inversions = countInversions(board);

        bool isInversionEven = inversions % 2 == 0;

        if (k % 2 == 1)
        {

            return isInversionEven;
        }
        else
        {
            int blankRow = BoardStructure::findBlank(board).first;

            int blankRowFromBottom = k - blankRow;

            bool isBlankRowEven = blankRowFromBottom % 2 == 0;

            return isInversionEven ^ isBlankRowEven;
        }
    }
};

class Heuristics

{

public:
    static int manhattanDistance(Board board, int k)

    {
        int distance = 0;

        for (int i = 0; i < board.size(); i++)

        {

            for (int j = 0; j < board[i].size(); j++)

            {

                if (board[i][j] == "0")

                {

                    continue;
                }
                int value = stoi(board[i][j]);

                int targetRow = (value - 1) / k;

                int targetCol = (value - 1) % k;

                distance += abs(i - targetRow) + abs(j - targetCol);
            }
        }

        return distance;
    }

    static int hammingDistance(Board board, int k)

    {

        int count = 0;

        for (int i = 0; i < board.size(); i++)

        {

            for (int j = 0; j < board[i].size(); j++)

            {

                if (board[i][j] == "0")

                {

                    continue;
                }

                int value = stoi(board[i][j]);

                if (value != i * k + j + 1)

                {

                    count++;
                }
            }
        }

        return count;
    }

    static int linearConflict(Board board, int k)

    {

        int distance = 0;

        int conflict_count = 0;

        unordered_map<int, pair<int, int>> current_positions;

        unordered_map<int, pair<int, int>> goal_positions;

        for (int i = 1; i <= k * k - 1; i++)

        {

            current_positions[i] = BoardStructure::findBlank(board);

            goal_positions[i] = BoardStructure::findBlank(board);
        }

        for (int i = 1; i <= k * k - 1; i++)

        {

            int current_row, current_col;

            int goal_row, goal_col;

            tie(current_row, current_col) = current_positions[i];

            tie(goal_row, goal_col) = goal_positions[i];

            if (current_row == goal_row)

            {
                if (current_row == 2 && goal_col == 2)
                {
                    continue;
                }

                for (int j = 1; j < i; j++)

                {

                    int pr, pc;

                    int gr, gc;

                    tie(pr, pc) = current_positions[j];

                    tie(gr, gc) = goal_positions[j];

                    if (current_row == pr && pr == gr)

                    {

                        if (current_col < pc && goal_col > gc)

                        {

                            conflict_count++;
                        }
                    }
                }
            }
        }

        distance = manhattanDistance(board, k) + 2 * conflict_count;

        return distance;
    }

    static int euclideanDistance(Board board, int k)

    {

        int distance = 0;

        for (int i = 0; i < board.size(); i++)

        {

            for (int j = 0; j < board[i].size(); j++)

            {

                if (board[i][j] == "0")

                {

                    continue;
                }

                int value = stoi(board[i][j]);

                int targetRow = (value - 1) / k;

                int targetCol = (value - 1) % k;

                distance += sqrt(pow(i - targetRow, 2) + pow(j - targetCol, 2));
            }
        }

        return distance;
    }
};

class AStarsolution

{

public:
    static void printSolution(shared_ptr<Node> node)

    {
        stack<shared_ptr<Node>> moves;
        shared_ptr<Node> current = node;

        while (current != nullptr)

        {

            moves.push(current);

            current = current->previous_state;
        }

        while (!moves.empty())

        {

            BoardStructure::printBoardElements(moves.top()->board);

            moves.pop();
        }
    }

    static void search(Board initial, Board goal, int k, int choice)

    {

        auto compare = [](shared_ptr<Node> a, shared_ptr<Node> b)

        {
            if (a->fn == b->fn)

            {
                if (a->hn == b->hn)
                {

                    return a->gn > b->gn;
                }

                return a->hn > b->hn;
            }

            return a->fn > b->fn;
        };

        priority_queue<shared_ptr<Node>, vector<shared_ptr<Node>>, decltype(compare)> open(compare);

        map<string, int> close;

        int explored_nodes = 0, expanded_nodes = 0;

        string goal_flat = BoardStructure::same_board(goal);

        open.push(make_shared<Node>(initial));

        explored_nodes++;

        while (!open.empty())

        {

            auto node = open.top();

            expanded_nodes++;

            open.pop();

            string board_flat = BoardStructure::same_board(node->board);

            close[board_flat] = node->fn;

            if (board_flat == goal_flat)

            {

                cout << "Minimum number of moves: " << node->gn << endl;

                cout << "Expanded nodes: " << expanded_nodes - 1 << endl;

                cout << "Explored nodes: " << explored_nodes << endl;

                printSolution(node);

                cout << "#######################################################" << endl;

                return;
            }

            for (int direction = 1; direction <= 4; direction++)

            {
                if (direction + node->previous_move != 5)

                {
                    auto position = BoardStructure::findBlank(node->board);

                    Board board = BoardStructure::moveDirection(node->board, direction, position.first, position.second);

                    int newActualCost = node->gn + 1;

                    int newEstimateCost = computeHeuristic(board, k, choice);

                    int newTotalCost = newActualCost + newEstimateCost;

                    int newHeuristic = newEstimateCost;

                    board_flat = BoardStructure::same_board(board);

                    if (close.find(board_flat) == close.end() || newTotalCost < close[board_flat])

                    {

                        shared_ptr<Node> newNode = make_shared<Node>(board, direction, node, newActualCost, newTotalCost, newHeuristic);

                        open.push(newNode);

                        explored_nodes++;

                        close[board_flat] = newTotalCost;
                    }
                }
            }
        }
    }

    static int computeHeuristic(Board board, int k, int distance)

    {

        if (distance == 0)
        {
            return Heuristics::hammingDistance(board, k);
        }

        else if (distance == 1)
        {
            return Heuristics::manhattanDistance(board, k);
        }
        else if (distance == 2)
        {
            return Heuristics::euclideanDistance(board, k);
        }
        else
        {
            return Heuristics::linearConflict(board, k);
        }
    }
};

class nPuzzle

{

private:
    int k;

    Board initial, goal;

public:
    nPuzzle(int k)

    {

        this->k = k;

        goal.resize(k);

        for (int i = 0; i < k; i++)

        {

            for (int j = 0; j < k; j++)

            {

                goal[i].push_back(to_string((i * k) + j + 1));
            }
        }

        goal[k - 1][k - 1] = "0";
    }

    void createBoard()

    {
        string value;

        initial.resize(k);

        for (int i = 0; i < k; i++)

        {

            for (int j = 0; j < k; j++)

            {

                cin >> value;

                initial[i].push_back(value);
            }
        }
    }

    void solve(int heuristic)

    {

        if (!SolvablePuzzle::isSolvable(initial, k))

        {

            cout << "Unsolvable puzzle" << endl;

            return;
        }
        else
        {

            cout << "Solvable puzzle" << endl;

            if (heuristic == 0)
            {
                cout << "Hamming Distance" << endl;
            }
            else if (heuristic == 1)
            {
                cout << "Manhattan Distance" << endl;
            }
            else if (heuristic == 2)
            {
                cout << "Linear Conflict" << endl;
            }
            else if (heuristic == 3)
            {
                cout << "Euclidean Distance" << endl;
            }
        }

        AStarsolution::search(initial, goal, k, heuristic);
    }
};
