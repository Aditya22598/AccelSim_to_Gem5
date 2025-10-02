import m5
from m5.objects import *

# --- Create the System ---

system = System()
# BlackParrot is often targeted for FPGAs, with clocks in the hundreds of MHz
system.clk_domain = SrcClockDomain(clock = '500MHz', voltage_domain = VoltageDomain())
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('2GB')]
system.membus = SystemXBar()

# --- Create the BlackParrot-like MinorCPU ---

# To model a dual-issue design, we provide multiple parallel functional units.
class BlackParrotFUPool(MinorFUPool):
    FUList = [
        MinorIntALU(),      # ALU for pipeline 0
        MinorIntALU(),      # ALU for pipeline 1
        MinorIntMultDiv(),  # Shared Multiplier/Divider
        MinorMemFU(),       # Memory access unit
        MinorFloatFU()      # Floating-point unit
    ]

cpu = MinorCPU()

# Set parameters for BlackParrot's pipeline
cpu.fetch1ToFetch2BufferSize = 1
cpu.fetch2ToDecodeBufferSize = 1
cpu.decodeToExecuteBufferSize = 2 # A slightly larger buffer for the dual-issue stage
cpu.executeToMemoryBufferSize = 1
cpu.memoryToWritebackBufferSize = 1

# Use a simple local branch predictor
cpu.branchPred = LocalBP()

# Assign the functional units that enable dual-issue execution
cpu.executeFuncUnits = BlackParrotFUPool()

# --- Create the Cache Hierarchy ---

system.cpu = cpu
# BlackParrot's default L1 caches are 32kB
system.cpu.icache = L1ICache(size='32kB')
system.cpu.dcache = L1DCache(size='32kB')
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

system.l2bus = L2XBar()
system.cpu.icache.connectBus(system.l2bus)
system.cpu.dcache.connectBus(system.l2bus)

system.l2cache = L2Cache(size='512kB')
system.l2cache.connectCPUSideBus(system.l2bus)
system.l2cache.connectMemSideBus(system.membus)

# --- Memory and Final Connections ---

system.system_port = system.membus.cpu_side_ports
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR4_2400_8x8()
system.mem_ctrl.port = system.membus.mem_side_ports

# --- Set up the process to run ---

# This should be a RISC-V executable, compiled with a RISC-V toolchain
# process = Process(cmd = ['path/to/riscv-executable'])
# system.cpu.workload = process
# system.cpu.createThreads()

# --- Instantiate and Run ---

root = Root(full_system = False, system = system)
m5.instantiate()

print("Beginning simulation of BlackParrot-like MinorCPU!")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")

