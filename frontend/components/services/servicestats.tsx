import ServiceCard from "@/components/services/servicecard"

async function getData() {
   const res = await fetch("http://127.0.0.1:5000/services", {
      next: { revalidate: 0 },
   })
   if (!res.ok) {
      throw new Error("Failed to fetch data")
   }
   return res.json()
}

export default async function ServiceStats() {
   const data = await getData()

   return (
      <div className="container mx-auto mt-12 mb-8">
         <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {Object.keys(data).map((service: string) => (
               <ServiceCard data={data[service]} />
            ))}
         </div>
      </div>
   )
}
