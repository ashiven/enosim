import VMCard from "@components/overview/vmcard"

export default function VMStats() {
   return (
      <div className="container mx-auto mt-12 mb-8">
         <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <VMCard name="Engine" />
            <VMCard name="Checker" />
            <VMCard name="Vulnbox1" />
            <VMCard name="Vulnbox2" />
            <VMCard name="Vulnbox3" />
         </div>
      </div>
   )
}
