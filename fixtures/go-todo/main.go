package main

import "fmt"
import "github.com/org/lib"

func main() {
    fmt.Println("start")
    helper()
}

func helper() {
    lib.Do()
}

func deadFunc() {
    fmt.Println("nunca chamado")
}
