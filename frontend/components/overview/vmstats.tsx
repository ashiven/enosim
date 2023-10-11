import VMCard from "@components/overview/vmcard"

export default function VMStats() {
   return (
      <div className="container mx-auto mt-12 mb-8">
         <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <VMCard
               data={{
                  name: "Engine",
                  status: "online",
                  cpu: "2 core intel idk",
                  memory: 2,
                  disk: 20,
                  uptime: 2223,
                  ip: "123.321.1.1",
               }}
            />
            <VMCard
               data={{
                  name: "Checker",
                  status: "offline",
                  cpu: "2 core intel idk",
                  memory: 2,
                  disk: 20,
                  uptime: 223,
                  ip: "123.321.1.1",
               }}
            />
            <VMCard
               data={{
                  name: "Vulnbox1",
                  status: "online",
                  cpu: "2 core intel idk",
                  memory: 2,
                  disk: 20,
                  uptime: 20,
                  ip: "123.321.1.1",
               }}
            />
            <VMCard
               data={{
                  name: "Vulnbox2",
                  status: "online",
                  cpu: "2 core intel idk",
                  memory: 2,
                  disk: 20,
                  uptime: 20,
                  ip: "123.321.1.1",
               }}
            />
            <VMCard
               data={{
                  name: "Vulnbox3",
                  status: "online",
                  cpu: "2 core intel idk",
                  memory: 2,
                  disk: 20,
                  uptime: 20,
                  ip: "123.321.1.1",
               }}
            />
            <VMCard
               data={{
                  name: "Engine",
                  status: "online",
                  cpu: "2 core intel idk",
                  memory: 2,
                  disk: 20,
                  uptime: 20,
                  ip: "123.321.1.1",
               }}
            />
         </div>
      </div>
   )
}
