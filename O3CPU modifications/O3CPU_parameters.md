**Frontend (Fetch, Decode, Rename)**

  * `fetchWidth`: Max instructions to fetch per cycle.
  * `decodeWidth`: Max instructions to decode per cycle.
  * `renameWidth`: Max instructions to rename per cycle.
  * `fetchBufferSize`: Number of instructions the fetch buffer can hold.
  * `fetchQueueSize`: Number of entries in the queue between fetch and decode.
  * `branchPred`: The branch predictor object to be used.

**Instruction Window & Dispatch**

  * `numROBEntries`: Number of entries in the Re-Order Buffer (tracks in-flight instructions).
  * `numIQEntries`: Number of entries in the main Issue Queue.
  * `dispatchWidth`: Max instructions to dispatch from rename to the issue queue per cycle.

**Execution & Functional Units**

  * `issueWidth`: Max instructions to issue from the IQ to functional units per cycle.
  * `executeWidth`: Max instructions that can begin execution per cycle.
  * `funcUnits`: A list of functional unit objects (ALUs, FPUs, etc.).
  * `LQEntries`: Number of entries in the Load Queue.
  * `SQEntries`: Number of entries in the Store Queue.

**Backend (Writeback & Commit)**

  * `wbWidth`: Max results to write back to physical registers per cycle.
  * `commitWidth`: Max instructions to commit (retire) from the ROB per cycle.
  * `numPhysIntRegs`: Number of physical registers for integer values.
  * `numPhysFloatRegs`: Number of physical registers for floating-point values.
  * `numPhysVecRegs`: Number of physical registers for vector values.

