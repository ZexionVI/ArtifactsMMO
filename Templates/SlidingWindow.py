import sys
from collections import deque

def sliding_window_minimum(n, k, sequence):
    # Дек для хранения индексов
    deq = deque()
    
    # Результат
    result = []
    
    for i in range(n):
        # Удаляем элементы, которые вышли за пределы окна
        if deq and deq[0] < i - k + 1:
            deq.popleft()
        
        # Удаляем элементы, которые больше текущего элемента
        while deq and sequence[deq[-1]] > sequence[i]:
            deq.pop()
        
        # Добавляем текущий элемент
        deq.append(i)
        
        # Записываем минимум текущего окна
        if i >= k - 1:
            result.append(sequence[deq[0]])
    
    return result

def main():
    # Чтение входных данных
    n, k = map(int, input().split())
    sequence = list(map(int, input().split()))

    # Получение результата
    result = sliding_window_minimum(n, k, sequence)

    # Вывод результата
    print("\n".join(map(str, result)))
    
    pass


if __name__ == '__main__':
    main()

#В первой строке вводится кол-во элементов в списке, а через пробел вводится размер окна.
#На следующей строке вводится сам список с элементами через пробел. По этому списку будет скользить окно.