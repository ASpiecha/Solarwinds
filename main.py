import lib

if __name__ == "__main__":
    reader = lib.Reader("input.csv")
    process = lib.Processor(reader.data)
    process.compute()
    lib.Writer(process.result)
