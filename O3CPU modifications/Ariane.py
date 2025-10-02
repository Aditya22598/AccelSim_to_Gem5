import m5
from m5.objects import *

# --- Create the System ---

system = System()
# Ariane is often synthesized for frequencies around 1.5GHz
system.clk_domain = SrcClockDomain(clock = '1.5GHz', voltage_domain = VoltageDomain())
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('2GB')]
system.membus = SystemXBar()

# --- Create the Ariane-like MinorCPU ---

# Define the functional units for Ariane's execute stage
class ArianeFUPool(MinorFUPool):
    FUList = [
        MinorIntALU(),
        MinorIntMultDiv(),
        MinorMemFU(),
        MinorFloatFU()
    ]

cpu = MinorCPU()

# Set parameters for Ariane's 6-stage, single-issue in-order pipeline
# We use buffer size 1 to model a tightly-coupled pipeline
cpu.fetch1ToFetch2BufferSize = 1
cpu.fetch2ToDecodeBufferSize = 1
cpu.decodeToExecuteBufferSize = 1
cpu.executeToMemoryBufferSize = 1
cpu.memoryToWritebackBufferSize = 1

# Use a simple local branch predictor to model Ariane's BHT/BTB
cpu.branchPred = LocalBP()

# Assign the functional units
cpu.executeFuncUnits = ArianeFUPool()

# --- Create the Cache Hierarchy ---

system.cpu = cpu
# Ariane's default L1 caches are 32kB
system.cpu.icache = L1ICache(size='32kB')
system.cpu.dcache = L1DCache(size='32kB')
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

system.l2bus = L2XBar()
system.cpu.icache.connectBus(system.l2bus)
system.cpu.dcache.connectBus(system.l2bus)

# Ariane is often paired with a 512kB L2 cache
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

print("Beginning simulation of Ariane-like MinorCPU!")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")

