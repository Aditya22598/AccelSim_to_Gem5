import m5
from m5.objects import *

# --- Create the System ---

system = System()
system.clk_domain = SrcClockDomain(clock = '2GHz', voltage_domain = VoltageDomain())
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('2GB')]
system.membus = SystemXBar()

# --- Create the BOOM-like O3 CPU ---

# First, define the list of functional units
class BoomFUPool(FUPool):
    FUList = [ IntALU(), IntMultDiv(), FP_ALU(), FP_MultDiv(), ReadPort(), WritePort() ]

cpu = O3CPU()

# Set parameters based on BOOM's known configuration
cpu.fetchWidth = 8
cpu.decodeWidth = 2
cpu.renameWidth = 2
cpu.dispatchWidth = 2
cpu.issueWidth = 4
cpu.wbWidth = 4
cpu.commitWidth = 2
cpu.executeWidth = 4

cpu.fetchBufferSize = 32
cpu.fetchQueueSize = 16
cpu.numROBEntries = 80
cpu.numIQEntries = 40

cpu.LQEntries = 24
cpu.SQEntries = 24

cpu.numPhysIntRegs = 100
cpu.numPhysFloatRegs = 96
cpu.numPhysVecRegs = 96 # Mapping FP to Vec registers as well

# Use a high-performance branch predictor to approximate BOOM's TAGE
cpu.branchPred = TournamentBP()

# Assign the functional units
cpu.fuPool = BoomFUPool()

# --- Create the Cache Hierarchy ---

system.cpu = cpu
system.cpu.icache = L1ICache(size='32kB')
system.cpu.dcache = L1DCache(size='32kB')
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

system.l2bus = L2XBar()
system.cpu.icache.connectBus(system.l2bus)
system.cpu.dcache.connectBus(system.l2bus)

system.l2cache = L2Cache(size='1MB')
system.l2cache.connectCPUSideBus(system.l2bus)
system.l2cache.connectMemSideBus(system.membus)

# --- Memory and Final Connections ---

system.system_port = system.membus.cpu_side_ports
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR4_2400_8x8() # Using a more modern DRAM
system.mem_ctrl.port = system.membus.mem_side_ports

# --- Set up the process to run ---

# This should be a RISC-V executable, since BOOM is a RISC-V core.
# We will need a RISC-V toolchain to compile it.
# For now, we will leave this blank as an example.
# process = Process(cmd = ['path/to/riscv-executable'])
# system.cpu.workload = process
# system.cpu.createThreads()

# --- Instantiate and Run ---

root = Root(full_system = False, system = system)
m5.instantiate()

print("Beginning simulation of BOOM-like O3CPU!")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")

