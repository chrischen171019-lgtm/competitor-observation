import { defineModule } from "@aihot/contracts/modules";
export default defineModule({
 name:"observation",
 apiPaths:[/^\/observe(?:\/|$)/,/^\/api\/observation(?:\/|$)/],
});
