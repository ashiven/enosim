import ContainerCharts from "@/components/containers/containercharts"
import ServiceStats from "@/components/services/servicestats"

import Navbar from "@components/navbar"
import Sidebar from "@components/sidebar"

export default function Home() {
   return (
      <main>
         <Navbar />
         <div className="flex">
            <Sidebar />
            <div className="container space-y-16">
               <ServiceStats />
               <ContainerCharts />
            </div>
         </div>
      </main>
   )
}
