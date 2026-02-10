# Check braces using stack

def bracesCorrect(text):
    stack = list()
    braces = ["(", ")"]
    for k in text:
        if(k not in braces):
            continue

        if(bool(stack)):
            top = stack[-1]
            if(braces.index(k) == 1 - braces.index(top)):
                stack.pop()
                continue
        
        stack.append(k)
    
    return not bool(stack)

text = input()
print(bracesCorrect(text))
