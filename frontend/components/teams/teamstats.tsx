import TeamCard from "@/components/teams/teamcard"

export async function getServerSideProps() {
   const res = await fetch(`http://127.0.0.1:5000/teams`)
   const data = await res.json()

   return { props: { data } }
}

export default function TeamStats({ data }: any) {
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
