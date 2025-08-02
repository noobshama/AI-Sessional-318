#include <bits/stdc++.h>
#include "2105045_nPuzzle.cpp"
using namespace std;

int main()
{

    freopen("output.txt", "w", stdout);

    int k;
    cin >> k;
    nPuzzle npuzzle(k);
    npuzzle.createBoard();

    npuzzle.solve(0);
    npuzzle.solve(1);
    npuzzle.solve(2);
    npuzzle.solve(3);

    fclose(stdout);
}
