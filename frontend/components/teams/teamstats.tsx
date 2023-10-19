import TeamCard from "@/components/teams/teamcard"

async function getData() {
   try {
      const res = await fetch("http://127.0.0.1:5000/teams", {
         next: { revalidate: 0 },
      })
      return res.json()
   } catch (e) {
      return {}
   }
}

export default async function TeamStats() {
   const data = await getData()

   return (
      <div className="container mx-auto mt-12 mb-8">
         <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {Object.keys(data).map((team: string) => (
               <TeamCard data={data[team]} />
            ))}
         </div>
      </div>
   )
}
