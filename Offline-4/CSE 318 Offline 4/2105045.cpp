#include <bits/stdc++.h>


using namespace std;


class DataPoint {


public:

    vector<string> features;

    string label;

    DataPoint() 

    {


    }

    DataPoint(vector<string> featureList, string classLabel) 

    {

        features = featureList;

        label = classLabel;
    }

    int getFeatureCount() 

    {

        return features.size();


    }

    void printDataPoint()

    {

        cout << "Features: ";

        for (int i = 0; i < features.size(); i++) {

            cout << features[i] << " ";

        }


        cout << "| Label: " << label << endl;

    }

};


class TreeNode 

{


public:

    bool isLeafNode;

    string leafLabel;

    int splitFeatureIndex;

    map<string, TreeNode*> childNodes;


    TreeNode() 

    {

        isLeafNode = false;

        splitFeatureIndex = -1;

        leafLabel = "";
    }

    void setAsLeaf(string label)

    {

        isLeafNode = true;

        leafLabel = label;
    }

    void setAsInternalNode(int featureIndex) 

    {

        isLeafNode = false;

        splitFeatureIndex = featureIndex;
        
    }

    void addChild(string featureValue, TreeNode* child) 

    {

        childNodes[featureValue] = child;

    }

    bool isLeaf()

    {

        return isLeafNode;


    }


    string getLabel() 

    {

        return leafLabel;

    }

    int getSplitFeature() 

    {

        return splitFeatureIndex;


    }


    TreeNode* getChild(string value) 

    {

        if (childNodes.find(value) != childNodes.end()) 

        {

            return childNodes[value];

        }

        return nullptr;

    }


    map<string, TreeNode*> getAllChildren() 

    {

        return childNodes;


    }

};
class DecisionTree 


{

private:


    vector<string> featureNames;

    string selectionCriterion;

    int maximumDepth;

    TreeNode* rootNode;

    int totalNodes;

    int actualTreeDepth;


    double calculateEntropy(vector<DataPoint> dataset) 

    {

        if (dataset.empty())

        {
            return 0.0;
        }

        map<string, int> labelCounts;

        for (int i = 0; i < dataset.size(); i++) 
        
        {
            labelCounts[dataset[i].label]++;
        }

        double entropy = 0.0;

        int totalDataPoints = dataset.size();

        for (map<string, int>::iterator it = labelCounts.begin(); it != labelCounts.end(); ++it) 
        {
            double probability = (double)it->second / totalDataPoints;
            if (probability > 0) 
            {
                entropy -= probability * log2(probability);
            }
        }
        return entropy;
    }
    double calculateInformationGain(vector<DataPoint> dataset, int featureIndex) 
    {
        double originalEntropy = calculateEntropy(dataset);

        map<string, vector<DataPoint>> subsets;

        for (int i = 0; i < dataset.size(); i++) {

            string featureValue = dataset[i].features[featureIndex];

            subsets[featureValue].push_back(dataset[i]);

        }


        double weightedEntropy = 0.0;

        int totalSize = dataset.size();

        for (map<string, vector<DataPoint>>::iterator it = subsets.begin(); it != subsets.end(); ++it) 
        
        {
            double weight = (double)it->second.size() / totalSize;

            double subsetEntropy = calculateEntropy(it->second);

            weightedEntropy += weight * subsetEntropy;

        }

        return originalEntropy - weightedEntropy;

    }

    double calculateIntrinsicValue(vector<DataPoint> dataset, int featureIndex) 
    
    {
        map<string, int> valueCounts;

        for (int i = 0; i < dataset.size(); i++) 
        
        {

            valueCounts[dataset[i].features[featureIndex]]++;


        }

        double intrinsicValue = 0.0;

        int totalSize = dataset.size();

        for (map<string, int>::iterator it = valueCounts.begin(); it != valueCounts.end(); ++it) 
        
        {
            double probability = (double)it->second / totalSize;

            if (probability > 0) {

                intrinsicValue -= probability * log2(probability);

            }

        }

        return intrinsicValue;

    }

    double calculateInformationGainRatio(vector<DataPoint> dataset, int featureIndex)
    
    {
        double informationGain = calculateInformationGain(dataset, featureIndex);

        double intrinsicValue = calculateIntrinsicValue(dataset, featureIndex);

        if (intrinsicValue == 0 || intrinsicValue < 1e-10)
        
        {

            return informationGain;


        }

        return informationGain / intrinsicValue;

    }

    double calculateNWIG(vector<DataPoint> dataset, int featureIndex) 
    
    {
        double informationGain = calculateInformationGain(dataset, featureIndex);

        set<string> uniqueValues;

        for (int i = 0; i < dataset.size(); i++) 
        {

            uniqueValues.insert(dataset[i].features[featureIndex]);

        }

        int k = uniqueValues.size();

        int datasetSize = dataset.size();

        if (k <= 1) 
        
        {

            return 0;
        }

        double penalty = (double)(k - 1) / datasetSize;


        double normalization = log2(k + 1);


        if (normalization == 0)
    
        {
            return 0;


        }

        return (informationGain / normalization) * (1 - penalty);

    }

    int selectBestFeature(vector<DataPoint> dataset, vector<bool> usedFeatures)
    
    {
        int bestFeature = -1;

        double bestScore = -1;

        for (int i = 0; i < featureNames.size(); i++)
        {
            if (usedFeatures[i])
            
            {

                continue;

            }

            double score = 0;

            if (selectionCriterion == "IG") 
            {
                score = calculateInformationGain(dataset, i);


            } 
            
            else if (selectionCriterion == "IGR") 
            {
               
                score = calculateInformationGainRatio(dataset, i);
            } 
            
            else if (selectionCriterion == "NWIG") 
            {
                score = calculateNWIG(dataset, i);
            }

            if (score > bestScore) 
            
            {
                bestScore = score;
                bestFeature = i;
            }
        }

        return bestFeature;
    }
       string findMajorityLabel(vector<DataPoint> dataset) 
       
       {
         map<string, int> labelCounts;
        for (int i = 0; i < dataset.size(); i++) 
        
        {
            labelCounts[dataset[i].label]++;
        }


        string majorityLabel = "";
        int maxCount = 0;


        for (map<string, int>::iterator it = labelCounts.begin(); it != labelCounts.end(); ++it) 
        {
            if (it->second > maxCount)
            
            {
                maxCount = it->second;
                majorityLabel = it->first;
            }
        }
        return majorityLabel;
    }
    bool allSameLabel(vector<DataPoint> dataset) 
    
    {
        if (dataset.empty()) 
        
        {
            return true;
        }
        string firstLabel = dataset[0].label;
        for (int i = 1; i < dataset.size(); i++) 
        {
            if (dataset[i].label != firstLabel) 
            
            {
                return false;
            }
        }
        return true;
    }
    TreeNode* buildDecisionTree(vector<DataPoint> dataset, vector<bool> usedFeatures, int currentDepth) 
    
    {
        totalNodes++;
        actualTreeDepth = max(actualTreeDepth, currentDepth);
        TreeNode* currentNode = new TreeNode();
        if (dataset.empty()) 
        
        {
            currentNode->setAsLeaf("unknown");
            return currentNode;
        }
        if (allSameLabel(dataset) || currentDepth == maximumDepth)
        
        {
            string majorityLabel = findMajorityLabel(dataset);
            currentNode->setAsLeaf(majorityLabel);
            return currentNode;
        }
        bool allFeaturesUsed = true;
        for (int i = 0; i < usedFeatures.size(); i++) 
        
        {
            if (!usedFeatures[i]) {
                allFeaturesUsed = false;
                break;
            }
        }
        if (allFeaturesUsed)
        
        {
            string majorityLabel = findMajorityLabel(dataset);
            currentNode->setAsLeaf(majorityLabel);
            return currentNode;
        }
        int bestFeature = selectBestFeature(dataset, usedFeatures);
        if (bestFeature == -1) 
        
        {
            string majorityLabel = findMajorityLabel(dataset);
            currentNode->setAsLeaf(majorityLabel);
            return currentNode;
        }
        currentNode->setAsInternalNode(bestFeature);
        usedFeatures[bestFeature] = true;
        map<string, vector<DataPoint>> subsets;
        for (int i = 0; i < dataset.size(); i++) 
        
        {
            string featureValue = dataset[i].features[bestFeature];
            subsets[featureValue].push_back(dataset[i]);
        }
        for (map<string, vector<DataPoint>>::iterator it = subsets.begin(); it != subsets.end(); ++it)
        
        {
            vector<bool> childUsedFeatures = usedFeatures;
            TreeNode* childNode = buildDecisionTree(it->second, childUsedFeatures, currentDepth + 1);
            currentNode->addChild(it->first, childNode);
        }
        usedFeatures[bestFeature] = false;
        return currentNode;
    }
    string predictSinglePoint(TreeNode* node, DataPoint dataPoint) 
    
    {
        if (node->isLeaf()) 
        
        {
            return node->getLabel();
        }
        string featureValue = dataPoint.features[node->getSplitFeature()];
        TreeNode* childNode = node->getChild(featureValue);
        if (childNode != nullptr) 
        
        {
            return predictSinglePoint(childNode, dataPoint);
        } 
        else 
        
        {
            map<string, TreeNode*> allChildren = node->getAllChildren();
            if (!allChildren.empty()) {
                return predictSinglePoint(allChildren.begin()->second, dataPoint);
            }
            return "unknown";
        }
    }


public:
    DecisionTree(string criterion, int maxDepth) 
    
    {
        selectionCriterion = criterion;
        maximumDepth = maxDepth;
        rootNode = nullptr;
        totalNodes = 0;
        actualTreeDepth = 0;
    }
    void trainTree(vector<DataPoint> trainingData, vector<string> features) 
    
    {
        featureNames = features;
        totalNodes = 0;
        actualTreeDepth = 0;
        vector<bool> usedFeatures(featureNames.size(), false);
        rootNode = buildDecisionTree(trainingData, usedFeatures, 0);
    }
    double evaluateAccuracy(vector<DataPoint> testData)
    
    {
        if (testData.empty()) 
        
        {
            return 0.0;
        }
        int correctPredictions = 0;
        for (int i = 0; i < testData.size(); i++) 
        
        {
            string predictedLabel = predictSinglePoint(rootNode, testData[i]);
            if (predictedLabel == testData[i].label) 
            
            {
                correctPredictions++;
            }
        }
        return (double)correctPredictions / testData.size();
    }
    int getNodeCount() 
    
    {
        return totalNodes;
    }
    int getTreeDepth() 
    
    {
        return actualTreeDepth;
    }
    void printTree(TreeNode* node, string indent) 
    
    {
        if (node == nullptr) return;
        if (node->isLeaf()) {
            cout << indent << "Leaf: " << node->getLabel() << endl;
        } else {
            cout << indent << "Split on feature " << node->getSplitFeature() << endl;
            map<string, TreeNode*> children = node->getAllChildren();
            for (map<string, TreeNode*>::iterator it = children.begin(); it != children.end(); ++it) {
                cout << indent << "  Value " << it->first << ":" << endl;
                printTree(it->second, indent + "    ");
            }
        }
    }
    void printTree()
    
    {
        printTree(rootNode, "");
    }
};
class DataLoader 

{
public:

    static vector<DataPoint> loadIrisDataset()
    
    {
        vector<DataPoint> dataset;
        ifstream inputFile("Datasets/Iris.csv");
        string line;
        getline(inputFile, line);
        while (getline(inputFile, line)) {
            stringstream lineStream(line);
            string item;
            DataPoint dataPoint;
            getline(lineStream, item, ',');
            for (int i = 0; i < 4; i++) {
                getline(lineStream, item, ',');
                dataPoint.features.push_back(item);
            }
            getline(lineStream, item);
            dataPoint.label = item;
            dataset.push_back(dataPoint);
        }
        inputFile.close();
        return dataset;
    }
    static vector<DataPoint> loadAdultDataset() 
    
    {
        vector<DataPoint> dataset;
        ifstream inputFile("Datasets/adult.data");
        string line;
        while (getline(inputFile, line)) {
            if (line.empty()) continue;
            stringstream lineStream(line);
            string item;
            vector<string> parts;
            while (getline(lineStream, item, ',')) {
                item.erase(0, item.find_first_not_of(" \t"));
                item.erase(item.find_last_not_of(" \t") + 1);
                parts.push_back(item);
            }
            if (parts.size() == 15) {
                DataPoint dataPoint;
                for (int i = 0; i < 14; i++) {
                    dataPoint.features.push_back(parts[i]);
                }
                dataPoint.label = parts[14];
                dataset.push_back(dataPoint);
            }
        }
        inputFile.close();
        return dataset;
    }


    static void discretizeNumericalFeatures(vector<DataPoint>& dataset, vector<bool> isNumerical) 
    
    {
        if (dataset.empty()) return;
        int numFeatures = dataset[0].getFeatureCount();
        for (int featureIndex = 0; featureIndex < numFeatures; featureIndex++) {
            if (!isNumerical[featureIndex]) continue;
            vector<double> numericalValues;
            for (int i = 0; i < dataset.size(); i++) {
                try {
                    double value = stod(dataset[i].features[featureIndex]);
                    numericalValues.push_back(value);
                } catch (...) {
                    numericalValues.push_back(0.0);
                }
            }
            sort(numericalValues.begin(), numericalValues.end());
            int n = numericalValues.size();
            double q1 = numericalValues[n/4];      
            double q2 = numericalValues[n/2];      
            double q3 = numericalValues[3*n/4];    
            for (int i = 0; i < dataset.size(); i++) {
                double value;
                try {
                    value = stod(dataset[i].features[featureIndex]);
                } catch (...) {
                    value = 0.0;
                }
                if (value <= q1) {
                    dataset[i].features[featureIndex] = "low";
                } else if (value <= q2) {
                    dataset[i].features[featureIndex] = "medium-low";
                } else if (value <= q3) {
                    dataset[i].features[featureIndex] = "medium-high";
                } else {
                    dataset[i].features[featureIndex] = "high";
                }
            }
        }
    }
    static pair<vector<DataPoint>, vector<DataPoint>> stratifiedSplit(vector<DataPoint> dataset, double trainRatio) 
    
    {
        map<string, vector<DataPoint>> classSeparatedData;
        for (int i = 0; i < dataset.size(); i++) {
            classSeparatedData[dataset[i].label].push_back(dataset[i]);
        }
        vector<DataPoint> trainingData, testingData;
        random_device randomDevice;
        mt19937 generator(randomDevice());
        for (map<string, vector<DataPoint>>::iterator it = classSeparatedData.begin(); 
             it != classSeparatedData.end(); ++it) {
            vector<DataPoint> classData = it->second;
            shuffle(classData.begin(), classData.end(), generator);
            int trainSize = (int)(classData.size() * trainRatio);
            for (int i = 0; i < trainSize; i++) {
                trainingData.push_back(classData[i]);
            }
            for (int i = trainSize; i < classData.size(); i++) {
                testingData.push_back(classData[i]);
            }
        }
        shuffle(trainingData.begin(), trainingData.end(), generator);
        shuffle(testingData.begin(), testingData.end(), generator);
        return make_pair(trainingData, testingData);
    }
};
int main(int argc, char* argv[]) 

{
    if (argc != 3) 
    {
        cout << "Usage: " << argv[0] << " <criterion> <maxDepth>" << endl;
        cout << "Criterion: IG, IGR, or NWIG" << endl;
        cout << "MaxDepth: integer (0 for no pruning)" << endl;
        return 1;
    }
    string criterion = argv[1];
    int maxDepth = atoi(argv[2]);
    if (maxDepth == 0) 
    {
        maxDepth = INT_MAX;
    }
    if (criterion != "IG" && criterion != "IGR" && criterion != "NWIG")
    
    {
        cout << "Invalid criterion. Use IG, IGR, or NWIG." << endl;
        return 1;
    }


    cout << "Decision Tree with " << criterion << " criterion, Max Depth: " << maxDepth << endl;
    cout << "================================================" << endl;
    cout << "\nIris Dataset Results:" << endl;
    vector<DataPoint> irisData = DataLoader::loadIrisDataset();
    vector<string> irisFeatureNames = {"SepalLength", "SepalWidth", "PetalLength", "PetalWidth"};
    vector<bool> irisNumericalFeatures = {true, true, true, true};
    DataLoader::discretizeNumericalFeatures(irisData, irisNumericalFeatures);
    double irisAccuracySum = 0.0;
    int irisNodeSum = 0;
    int irisDepthSum = 0;
    for (int run = 1; run <= 20; run++) 
    
    {
        pair<vector<DataPoint>, vector<DataPoint>> split = DataLoader::stratifiedSplit(irisData, 0.8);
        vector<DataPoint> trainData = split.first;
        vector<DataPoint> testData = split.second;
        DecisionTree tree(criterion, maxDepth);
        tree.trainTree(trainData, irisFeatureNames);
        
        double accuracy = tree.evaluateAccuracy(testData);
        irisAccuracySum += accuracy;
        irisNodeSum += tree.getNodeCount();
        irisDepthSum += tree.getTreeDepth();
        cout << "Run " << run << ": Accuracy = " << fixed << setprecision(2) << accuracy * 100 << "%" 
             << ", Nodes = " << tree.getNodeCount() << ", Depth = " << tree.getTreeDepth() << endl;
    }
    cout << "Average Accuracy: " << fixed << setprecision(2) << (irisAccuracySum / 20) * 100 << "%" << endl;
    cout << "Average Nodes: " << irisNodeSum / 20 << endl;
    cout << "Average Depth: " << irisDepthSum / 20 << endl;
    cout << "\nAdult Dataset Results:" << endl;
    vector<DataPoint> adultData = DataLoader::loadAdultDataset();
    vector<string> adultFeatureNames;
    for (int i = 0; i < 14; i++)
    
    {
        adultFeatureNames.push_back("feature" + to_string(i));
    }


    vector<bool> adultNumericalFeatures = {true, false, true, false, true, false, false, false, false, false, true, true, true, false};
    DataLoader::discretizeNumericalFeatures(adultData, adultNumericalFeatures);
    double adultAccuracySum = 0.0;
    int adultNodeSum = 0;
    int adultDepthSum = 0;
    for (int run = 1; run <= 20; run++) 
    
    {
        pair<vector<DataPoint>, vector<DataPoint>> split = DataLoader::stratifiedSplit(adultData, 0.8);

        vector<DataPoint> trainData = split.first;

        vector<DataPoint> testData = split.second;

        DecisionTree tree(criterion, maxDepth);

        tree.trainTree(trainData, adultFeatureNames);

        double accuracy = tree.evaluateAccuracy(testData);

        adultAccuracySum += accuracy;
        
        adultNodeSum += tree.getNodeCount();
        adultDepthSum += tree.getTreeDepth();
        cout << "Run " << run << ": Accuracy = " << fixed << setprecision(2) << accuracy * 100 << "%" 
             << ", Nodes = " << tree.getNodeCount() << ", Depth = " << tree.getTreeDepth() << endl;
    }
    cout << "Average Accuracy: " << fixed << setprecision(2) << (adultAccuracySum / 20) * 100 << "%" << endl;
    cout << "Average Nodes: " << adultNodeSum / 20 << endl;
    cout << "Average Depth: " << adultDepthSum / 20 << endl;
    return 0;
}
