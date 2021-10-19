# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import time

import graph

import graphNew

import graphNavie


# Press the green button in the gutter to run the script.

# 判断新方法相似矩阵计算是否正确
def verifySimilarity(graph):
    graph1 = graphNew.Graph('mintest.txt')
    graph1.calculateWords()
    graph1.calculateTFIDF()
    graph1.calculateArticleVector()
    graph1.calculateSimilarityMatrix()

    a = graph.getSimilarityMatrix()
    b = graph1.getSimilarityMatrix()

    for i in range(len(a)):
        if a[i] - b[i] < 0.00000001:
            continue
        else:
            return False
    return True


def verify(graphNew, graph):
    if len(graphNew.getArticleNodes()) != len(graph.getArticleNodes()):
        print("articleNodes not the same")
        return False
    if len(graphNew.getWordCount()) != len(graph.getWordCount()):
        print("wordCount not the same")
        return False
    if len(graphNew.getWordArticleNodes()) != len(graph.getWordArticleNodes()):
        print("wordArticleNodes not the same")
        return False
    # 判断articleNodes的正确性
    a = graphNew.getArticleNodes()
    b = graph.getArticleNodes()
    # print(len(a),len(b))
    for i in range(len(a)):
        tempA = a[i]
        tempB = b[i]

        if tempA != tempB:
            print("article node is not the same")

            return False
            # print(a[i])
            # print(b[i])
            # print('\n')
    if graph.getWordCount() != graphNew.getWordCount():
        print("word count")
        return False
    if graph.getWordArticleNodes() != graphNew.getWordArticleNodes():
        print("word article nodes")
        return False
    # print(len(graph.getArticleIndex()))
    # print(len(graphNew.getArticleIndex()))
    if graph.getArticleIndex() != graphNew.getArticleIndex():
        print("articleIndex is not the same")
        return False
    if graph.getArticleTFIDF() != graphNew.getArticleTFIDF():
        print("article tfidf is not the same")
        return False
    if graph.articleVector != graphNew.articleVector:
        print("article vector is not the same")
        return False
    if graphNew.getSimilarityMatrix() != graph.getSimilarityMatrix():
        print(" similarity matrxi is not the same")
    return True


if __name__ == '__main__':

    print("------ 采用并发方式的时间消耗情况 -------")
    graphNew = graphNew.Graph('test/test-1.txt')
    time_start = time.time()
    graphNew.calculateWords()
    time_end = time.time()
    print('第一步执行时间', time_end - time_start, 's')

    time_start = time.time()
    graphNew.calculateTFIDF()
    time_end = time.time()
    print('第二步执行时间', time_end - time_start, 's')

    time_start = time.time()
    graphNew.calculateArticleVector()
    time_end = time.time()
    print('第三步执行时间', time_end - time_start, 's')

    time_start = time.time()
    graphNew.calculateSimilarityMatrixNew()
    time_end = time.time()
    print("第四步执行时间", time_end - time_start, 's')

    time_start = time.time()
    graphNew.writeSimilarityMatrix()
    time_end = time.time()
    print("第五步执行时间", time_end - time_start, 's')

    print("------ 提高数据处理质量和克服矩阵稀疏性的时间消耗情况 -------")
    graph = graph.Graph('test.txt')
    time_start = time.time()
    graph.calculateWords()
    time_end = time.time()
    print('第一步执行时间', time_end - time_start, 's')

    time_start = time.time()
    graph.calculateTFIDF()
    time_end = time.time()
    print('第二步执行时间', time_end - time_start, 's')

    time_start = time.time()
    graph.calculateArticleVector()
    time_end = time.time()
    print('第三步执行时间', time_end - time_start, 's')

    time_start = time.time()
    graph.calculateSimilarityMatrix()
    time_end = time.time()
    print("第四步执行时间", time_end - time_start, 's')

    time_start = time.time()
    graph.writeSimilarityMatrix()
    time_end = time.time()
    print("第五步执行时间", time_end - time_start, 's')

    print("------ 最为朴素方式的时间消耗情况 -------")
    graphNavie = graphNavie.Graph('test.txt')
    time_start = time.time()
    graphNavie.calculateWords()
    time_end = time.time()
    print('第一步执行时间', time_end - time_start, 's')

    time_start = time.time()
    graphNavie.calculateTFIDF()
    time_end = time.time()
    print('第二步执行时间', time_end - time_start, 's')

    time_start = time.time()
    graphNavie.calculateArticleVector()
    time_end = time.time()
    print('第三步执行时间', time_end - time_start, 's')

    time_start = time.time()
    graphNavie.calculateSimilarityMatrix()
    time_end = time.time()
    print("第四步执行时间", time_end - time_start, 's')

    # print(verify(graphNew, graph))


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
