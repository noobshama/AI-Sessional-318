#include <iostream>
#include <fstream>
#include <vector>
#include <random>
#include <algorithm>
#include <bits/stdc++.h>

using namespace std;

#define INF 1e9

vector<vector<pair<int, int>>> adj;
vector<pair<int, pair<int, int>>> edgelist;
int n, m;

random_device rd;
mt19937 gen(rd());
uniform_int_distribution<> dis(0, 1);

int max_edge_weight = -INF;
int min_edge_weight = INF;

vector<int> generate_random_values(int size)
{
    vector<int> values(size);
    for (int i = 0; i < size; ++i)
    {
        values[i] = dis(gen);
    }
    return values;
}

int calculate_cut_weight(const vector<int> &vertex_set_map)
{
    int cut = 0;
    for (auto &edge : edgelist)
    {
        int u = edge.second.first;
        int v = edge.second.second;
        int weight = edge.first;
        if (vertex_set_map[u] != vertex_set_map[v])
        {
            cut += weight;
        }
    }
    return cut;
}

int new_vertex_cut_calc(const vector<int> &vertex_set_map, int partition, int new_vertex)
{
    int cut = 0;
    for (auto &neighbor : adj[new_vertex])
    {
        int v = neighbor.first;
        int weight = neighbor.second;
        if (vertex_set_map[v] != partition)
        {
            cut += weight;
        }
    }
    return cut;
}

int greedy_max_cut(int n)
{
    vector<int> vertex_set_map(n + 1, -1);

    int max_edge_weight = -INF;
    int u_max = -1, v_max = -1;

    for (auto &edge : edgelist)
    {
        int u = edge.second.first;
        int v = edge.second.second;
        int weight = edge.first;

        if (weight > max_edge_weight)
        {
            max_edge_weight = weight;
            u_max = u;
            v_max = v;
        }
    }

    vertex_set_map[u_max] = 0;
    vertex_set_map[v_max] = 1;

    for (int i = 1; i <= n; ++i)
    {
        if (vertex_set_map[i] == -1)
        {

            int cut_contribution_X = 0, cut_contribution_Y = 0;

            for (auto &neighbor : adj[i])
            {
                int v = neighbor.first;
                int weight = neighbor.second;

                if (vertex_set_map[v] == 0)
                    cut_contribution_Y += weight;
                else if (vertex_set_map[v] == 1)
                    cut_contribution_X += weight;
            }

            if (cut_contribution_X > cut_contribution_Y)
                vertex_set_map[i] = 0;
            else
                vertex_set_map[i] = 1;
        }
    }

    return calculate_cut_weight(vertex_set_map);
}

int randomized_max_cut(int n, int iterations)
{
    int total_cut_weight = 0;

    for (int i = 0; i < iterations; i++)
    {
        vector<int> vertex_set_map(n + 1, 0);

        for (int j = 1; j <= n; j++)
        {
            vertex_set_map[j] = dis(gen);
        }

        int cut_weight = calculate_cut_weight(vertex_set_map);
        total_cut_weight += cut_weight;
    }

    return total_cut_weight / iterations;
}

pair<vector<int>, int> semi_greedy(int heuristic = 2, bool greedy = false)
{
    double alpha = 1;
    if (!greedy)
        alpha = dis(gen) * 1.0 / 100;

    int threshold = min_edge_weight + alpha * (max_edge_weight - min_edge_weight);

    vector<int> rcl;
    vector<int> vertex_set_map(n + 1, -1);

    for (int i = 0; i < edgelist.size(); i++)
        if (edgelist[i].first >= threshold)
            rcl.push_back(i);

    if (rcl.empty())
    {
        int initial_edge = dis(gen) % edgelist.size();
        vertex_set_map[edgelist[initial_edge].second.first] = 0;
        vertex_set_map[edgelist[initial_edge].second.second] = 1;
    }
    else
    {
        int initial_edge = rcl[dis(gen) % rcl.size()];
        vertex_set_map[edgelist[initial_edge].second.first] = 0;
        vertex_set_map[edgelist[initial_edge].second.second] = 1;
    }

    int vertex_count = 2;

    while (vertex_count < n)
    {
        vector<int> sigmax(n + 1, 0);
        vector<int> sigmay(n + 1, 0);
        vector<int> score(n + 1, 0);
        vector<int> rcl;

        int wmax = -INF;
        int wmin = INF;

        for (int i = 1; i <= n; i++)
        {
            if (vertex_set_map[i] == -1)
            {
                int cut1 = new_vertex_cut_calc(vertex_set_map, 0, i);
                int cut2 = new_vertex_cut_calc(vertex_set_map, 1, i);

                if (heuristic == 2)
                    score[i] = abs(cut1 - cut2);
                else
                    score[i] = max(cut1, cut2);

                wmax = max(wmax, score[i]);
                wmin = min(wmin, score[i]);

                sigmax[i] = cut1;
                sigmay[i] = cut2;
            }
        }

        threshold = wmin + alpha * (wmax - wmin);

        for (int i = 1; i <= n; i++)
        {
            if (vertex_set_map[i] == -1 && score[i] >= threshold)
            {
                rcl.push_back(i);
            }
        }

        if (rcl.empty())
        {
            int random_vertex = dis(gen) % n + 1;
            if (sigmax[random_vertex] >= sigmay[random_vertex])
                vertex_set_map[random_vertex] = 0;
            else
                vertex_set_map[random_vertex] = 1;

            vertex_count++;
            continue;
        }

        int new_vertex = rcl[dis(gen) % rcl.size()];
        vertex_set_map[new_vertex] = (sigmax[new_vertex] >= sigmay[new_vertex]) ? 0 : 1;

        vertex_count++;
    }

    int cut = 0;
    for (int i = 1; i <= n; i++)
    {
        if (vertex_set_map[i] == 0)
            cut += new_vertex_cut_calc(vertex_set_map, 0, i);
    }

    return {vertex_set_map, cut};
}

int delta(int v, const vector<int> &vertex_set_map)
{
    int sigma_S = 0, sigma_not_S = 0;

    for (auto &neighbor : adj[v])
    {
        int u = neighbor.first;
        int weight = neighbor.second;

        if (vertex_set_map[u] == 0)
            sigma_S += weight; // u in S
        else
            sigma_not_S += weight; // u in not S
    }

    if (vertex_set_map[v] == 0) // v in S
        return sigma_S - sigma_not_S;
    else // v in not S
        return sigma_not_S - sigma_S;
}

int local_search(const vector<int> &vertex_set_map)
{
    vector<int> current_map = vertex_set_map;
    bool change = true;
    while (change)
    {
        change = false;

#pragma omp parallel for
        for (int v = 1; v <= n; v++)
        {
            int current_delta = delta(v, current_map);

            if (current_delta > 0)
            {
                current_map[v] = 1 - current_map[v]; // Toggle between 0 and 1
                change = true;
            }
        }
    }

    return calculate_cut_weight(current_map); // Return the final cut value after local search
}

// GRASP algorithm implementation with Average Local Search Cut Value
pair<pair<vector<int>, int>, int> GRASP(int max_iterations)
{
    pair<vector<int>, int> best_solution;
    best_solution.second = -INF; // Start with a very low value to find a better one.

    // Variable to track total local search cut values
    int total_local_search_value = 0;

#pragma omp parallel for
    for (int i = 0; i < max_iterations; ++i)
    {
        // Step 1: Construct a greedy randomized solution
        pair<vector<int>, int> current_solution = semi_greedy();

        // Step 2: Apply local search to the solution
        current_solution.second = local_search(current_solution.first);

        // Step 3: Update the best solution if the current one is better
        if (i == 0 || current_solution.second > best_solution.second)
        {
            best_solution = current_solution;
        }

        // Track the value from the local search
        total_local_search_value += current_solution.second;
    }

    // Calculate the average value of local search cuts
    int average_local_search_value = total_local_search_value / max_iterations;

    return {best_solution, average_local_search_value};
}

int main(int argc, char *argv[])
{
    ofstream output_file("results.csv");
    output_file << "Problem,,,Constructive Algorithm,,,Local Search,,Grasp,,Known Best Solution or Upper Bound\n";
    output_file << "Name,|V|,|E|,Randomized-1,Greedy-1, Semi-Greedy-1,LS-iterations,LS-avg-value,GRASP-iterations,GRASP-best-value,Best Value\n";

#pragma omp parallel for schedule(dynamic)
    for (int file_id = 1; file_id <= 54; ++file_id)
    {
        string file_name = "g" + to_string(file_id) + ".rud";
        ifstream input_file(file_name);

        if (!input_file.is_open())
        {
            cerr << "Failed to open file: " << file_name << endl;
            continue;
        }

        input_file >> n >> m;

        adj.clear();
        adj.resize(n + 1);
        edgelist.clear();

        max_edge_weight = -INF;
        min_edge_weight = INF;

        for (int i = 0; i < m; ++i)
        {
            int u, v, w;
            input_file >> u >> v >> w;
            adj[u].push_back({v, w});
            adj[v].push_back({u, w});
            edgelist.push_back({w, {u, v}});
            max_edge_weight = max(max_edge_weight, w);
            min_edge_weight = min(min_edge_weight, w);
        }

        input_file.close();

        int greedy_cut_result = greedy_max_cut(n);
        int randomized_cut_result = randomized_max_cut(n, n);
        pair<vector<int>, int> result = semi_greedy(2, false);

        // Declaration of best_grasp_solution and average_local_search_value
        pair<vector<int>, int> best_grasp_solution; // to store the best solution (vertex set map and its corresponding cut value)
        int average_local_search_value;             // to store the average value of local search cuts

        int grasp_iterations = 300;
        pair<pair<vector<int>, int>, int> grasp_result = GRASP(grasp_iterations);

        // Assigning results from GRASP
        best_grasp_solution = grasp_result.first;
        average_local_search_value = grasp_result.second;
        output_file << "g" + to_string(file_id) << "," << n << "," << m << ","
                    << randomized_cut_result << "," << greedy_cut_result << "," << result.second << "," << grasp_iterations << "," << average_local_search_value << "," << grasp_iterations << "," << best_grasp_solution.second << "," << "N/A"
                                                                                                                                                                                                                                           "\n";
    }

    output_file.close();

    return 0;
}
