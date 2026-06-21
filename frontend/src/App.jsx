import { BrowserRouter, Routes, Route } from "react-router-dom";

import Layout from "./components/Layout";
import Upload from "./pages/Upload";
import Dashboard from "./pages/Dashboard";
import Chat from "./pages/Chat";


function App(){

return (
<BrowserRouter>

<Layout>

<Routes>

<Route path="/" element={<Dashboard/>}/>

<Route path="/upload" element={<Upload/>}/>

<Route path="/dashboard" element={<Dashboard/>}/>

<Route path="/chat" element={<Chat/>}/>

</Routes>

</Layout>

</BrowserRouter>
)

}


export default App;
