# 2026-08-09 实验源码清单

本目录只保存可直接阅读、比较和编译的完整 `.cpp` 候选源码。原有 22 个差分归档已按各自父源码依次还原；还原后的 SHA-256 与 `notes.md` 中实验时记录的候选 SHA 全部一致，原差分文件已删除。差分文件不得再作为实验的唯一归档。

详细假设、correctness、资源用量和交错 A/B 数据见仓库根目录的 [`notes.md`](../../../notes.md)。这里的状态只表示该候选本身的实验结论；`positive` 不代表已经成为 OJ baseline。

| 实验 | 完整源码 | 父源码（SHA-256） | 候选 SHA-256 | 状态 |
|---|---|---|---|---|
| exp6 | [`cuda_case11_warp32_state_elision.cpp`](cuda_case11_warp32_state_elision.cpp) | #106069 (`a8101a3f2f78b00129c575af42cf2a945f4d057fcb869ef4ae1a779837d38deb`) | `e9b4d6576f639fd96873968d2bed40ff6366afd232ee39062b75202b955970a9` | rejected（资源门槛） |
| exp8 | [`cuda_case11_qk_wave8_interleave.cpp`](cuda_case11_qk_wave8_interleave.cpp) | #106069 (`a8101a3f2f78b00129c575af42cf2a945f4d057fcb869ef4ae1a779837d38deb`) | `e12c22a8921bc647d615b282431e242d3d0a09b836402acf3a93da540cef1ee4` | rejected |
| exp8 | [`cuda_case11_qk_group4_interleave.cpp`](cuda_case11_qk_group4_interleave.cpp) | #106069 (`a8101a3f2f78b00129c575af42cf2a945f4d057fcb869ef4ae1a779837d38deb`) | `57bdb333b72fef22902a8bc088eff0bdbc729a7a4503e924f0ad7d0890fede78` | rejected |
| exp10 | [`cuda_case11_head4_z4.cpp`](cuda_case11_head4_z4.cpp) | #106069 (`a8101a3f2f78b00129c575af42cf2a945f4d057fcb869ef4ae1a779837d38deb`) | `2a873decfbf2d2fbe222614cdc487e9a2e768b4998b1e3797d0e1125afa213b0` | rejected |
| exp11 | [`cuda_case11_split_qk_acc.cpp`](cuda_case11_split_qk_acc.cpp) | #106069 (`a8101a3f2f78b00129c575af42cf2a945f4d057fcb869ef4ae1a779837d38deb`) | `c8d118ad6e1b75dd3550f4a58db9867ea07113622ad272c3b0fa068b606e0f81` | rejected |
| exp12 | [`cuda_case11_bitcast_qk.cpp`](cuda_case11_bitcast_qk.cpp) | #106069 (`a8101a3f2f78b00129c575af42cf2a945f4d057fcb869ef4ae1a779837d38deb`) | `5f7d2178ae4cdd8cffbec88502b458f930ebbf11a56cadd2ccff6b67d6176549` | neutral |
| exp17 | [`cuda_case8_headpair_z4.cpp`](cuda_case8_headpair_z4.cpp) | #106626 (`bc5b3a4de04e68161342b902c901deb480c358e1b2cc3c8280ec44b0f125c5f3`) | `fb2e0ca452ef8b39b204e8a172d9afec3f12b010924a245d4947ad0e7d725db3` | positive，OJ pending |
| exp18 | [`cuda_case11_headpair_z4_split48.cpp`](cuda_case11_headpair_z4_split48.cpp) | exp17 (`fb2e0ca452ef8b39b204e8a172d9afec3f12b010924a245d4947ad0e7d725db3`) | `445e7046bd994d186d72957dcbd55fe16fa6549797528f0bd3b63db6bc55cff3` | positive，等待 OJ 判定 |
| exp19 | [`cuda_case14_headpair_z4_combined.cpp`](cuda_case14_headpair_z4_combined.cpp) | exp18 (`445e7046bd994d186d72957dcbd55fe16fa6549797528f0bd3b63db6bc55cff3`) | `7308ce75392ef5ae4e2ed242d42b354c8f78483adb8929098fb1e8b64894f922` | rejected |
| exp20 | [`cuda_case14_split257.cpp`](cuda_case14_split257.cpp) | exp18 (`445e7046bd994d186d72957dcbd55fe16fa6549797528f0bd3b63db6bc55cff3`) | `42cb6e435ec93f8a07ccf001a798d5637882c0b64f30348ea04ea2bd01410c99` | positive，等待 OJ 判定 |
| exp21 | [`cuda_case10_split171.cpp`](cuda_case10_split171.cpp) | exp20 (`42cb6e435ec93f8a07ccf001a798d5637882c0b64f30348ea04ea2bd01410c99`) | `aa61eddec96ad5a4c886a4e4fdb5d21cbc88c123e0eda083a08e2eb4fbcc0b2f` | rejected |
| exp22 | [`cuda_case5_split5.cpp`](cuda_case5_split5.cpp) | exp20 (`42cb6e435ec93f8a07ccf001a798d5637882c0b64f30348ea04ea2bd01410c99`) | `e4827a6542fe9e7280d7a746d56a242311584323ed5f9c47fa843abc335cde8e` | positive，等待 OJ 判定 |
| exp23 | [`cuda_case6_split12.cpp`](cuda_case6_split12.cpp) | exp22 (`e4827a6542fe9e7280d7a746d56a242311584323ed5f9c47fa843abc335cde8e`) | `98704dd09e17e2ccf18794558dd40ac4bd46c4535f437658228b4fb81e6b057b` | rejected |
| exp24 | [`cuda_case13_split264.cpp`](cuda_case13_split264.cpp) | exp22 (`e4827a6542fe9e7280d7a746d56a242311584323ed5f9c47fa843abc335cde8e`) | `06f18cfeb5fe51513c2d8c1c0954b9fca73a0ee6f6ce87ea831042a327a3cb2f` | rejected |
| exp25 | [`cuda_case8_headpair_z4_split52.cpp`](cuda_case8_headpair_z4_split52.cpp) | exp22 (`e4827a6542fe9e7280d7a746d56a242311584323ed5f9c47fa843abc335cde8e`) | `2e065e528196ddd8c0ff3dc7cd96a3a563f8f25fe588ed96e93c082b37cdfaa5` | rejected |
| exp25 | [`cuda_case8_headpair_z4_split43.cpp`](cuda_case8_headpair_z4_split43.cpp) | exp22 (`e4827a6542fe9e7280d7a746d56a242311584323ed5f9c47fa843abc335cde8e`) | `d47ce21692873581282ad72aee184bf31aacfee9f64bf1ce09070eafdd128b70` | neutral |
| exp26 | [`cuda_case11_group8_reduce49.cpp`](cuda_case11_group8_reduce49.cpp) | exp22 (`e4827a6542fe9e7280d7a746d56a242311584323ed5f9c47fa843abc335cde8e`) | `dbff3f247fbcd382f4a8b3ef0ea3f17b8a1ec7a727d8c2a6c45ecfb15fddff83` | neutral |
| exp27 | [`cuda_case5_headpair_z4_combined.cpp`](cuda_case5_headpair_z4_combined.cpp) | exp22 (`e4827a6542fe9e7280d7a746d56a242311584323ed5f9c47fa843abc335cde8e`) | `8f7ad8b8d5ffa1cd8fae465b53b5853ea44fb86019664574f896c8ec4dda4120` | rejected |
| exp28 | [`cuda_case14_inplace_q_split257.cpp`](cuda_case14_inplace_q_split257.cpp) | exp22 (`e4827a6542fe9e7280d7a746d56a242311584323ed5f9c47fa843abc335cde8e`) | `215bd318e4f7be1cdeb2f55af35a1ded6510a0062e62ce233778c48158cd714c` | neutral |
| exp29 | [`cuda_case14_sync_loader_split257.cpp`](cuda_case14_sync_loader_split257.cpp) | exp22 (`e4827a6542fe9e7280d7a746d56a242311584323ed5f9c47fa843abc335cde8e`) | `8d4a66322ff1b4debfbc7bb645f772b776da25b370df9899c74c602e8d30c924` | rejected |
| exp31 | [`cuda_case14_pair32_broadcast.cpp`](cuda_case14_pair32_broadcast.cpp) | exp22 (`e4827a6542fe9e7280d7a746d56a242311584323ed5f9c47fa843abc335cde8e`) | `dd73f669812f489ec0d6cbc4d801735d9153dd496c12d1aeb3c4bc73c7ef2a92` | rejected |
| exp32 | [`cuda_case14_headpair_z4_split257.cpp`](cuda_case14_headpair_z4_split257.cpp) | exp22 (`e4827a6542fe9e7280d7a746d56a242311584323ed5f9c47fa843abc335cde8e`) | `86fae30ec819a259bf278af9d834568f437f7fe26f9a51e9a3c3985ace003b9c` | rejected |
| exp33 | [`cuda_case14_reducer_vec2.cpp`](cuda_case14_reducer_vec2.cpp) | exp22 (`e4827a6542fe9e7280d7a746d56a242311584323ed5f9c47fa843abc335cde8e`) | `acf1b18463a7a476ac4c66deff36bb75f2066275025313a41707c79ce4390f98` | neutral |
| exp34 | [`cuda_headpair_stage2_row8.cpp`](cuda_headpair_stage2_row8.cpp) | exp22 (`e4827a6542fe9e7280d7a746d56a242311584323ed5f9c47fa843abc335cde8e`) | `ab15fc5100c9b25cefed05a604ad32de722163245238bf54b5bc8acab285155a` | neutral |
| exp35 | [`cuda_headpair_direct_q.cpp`](cuda_headpair_direct_q.cpp) | exp22 (`e4827a6542fe9e7280d7a746d56a242311584323ed5f9c47fa843abc335cde8e`) | `c86788872a0513d63d3f61f7d8c2d9eba487ead2467b00f3943339c1859cf040` | positive，OJ 暂停提交 |
| exp36 | [`cuda_case14_bf16_normalized_partial.cpp`](cuda_case14_bf16_normalized_partial.cpp) | exp35 (`c86788872a0513d63d3f61f7d8c2d9eba487ead2467b00f3943339c1859cf040`) | `eab62e0e84f538ac75ff0bda8835349f3f8c9c3682598dba56cd4ccfd17f1bd6` | positive，已被 exp56 取代 |
| exp37 | [`cuda_case14_bf16_normalized_partial_vec2.cpp`](cuda_case14_bf16_normalized_partial_vec2.cpp) | exp36 (`eab62e0e84f538ac75ff0bda8835349f3f8c9c3682598dba56cd4ccfd17f1bd6`) | `bc01c38bb6da292b0dc9afd985c91c85d4536aaaaccfb21cb33c85fe8d3fc09c` | rejected |
| exp38 | [`cuda_case13_bf16_normalized_partial.cpp`](cuda_case13_bf16_normalized_partial.cpp) | exp36 (`eab62e0e84f538ac75ff0bda8835349f3f8c9c3682598dba56cd4ccfd17f1bd6`) | `61941a8de6e6a8c307e80be5596322547010be50ef845593b9d8d4a7f8726c0d` | rejected |
| exp39 | [`cuda_case12_bf16_normalized_partial.cpp`](cuda_case12_bf16_normalized_partial.cpp) | exp36 (`eab62e0e84f538ac75ff0bda8835349f3f8c9c3682598dba56cd4ccfd17f1bd6`) | `41c8d2049228dc32208872d3c34b62706d836959609e45219bd5df88769d218a` | rejected |
| exp40 | [`cuda_case14_bf16_raw_partial.cpp`](cuda_case14_bf16_raw_partial.cpp) | exp36 (`eab62e0e84f538ac75ff0bda8835349f3f8c9c3682598dba56cd4ccfd17f1bd6`) | `5d8f931db05420bedf000d7f51bfa0b5fa2a4dfb84a560f925d0a1a04a1c42f4` | neutral vs normalized |
| exp41 | [`cuda_case14_fp16_normalized_partial.cpp`](cuda_case14_fp16_normalized_partial.cpp) | exp36 (`eab62e0e84f538ac75ff0bda8835349f3f8c9c3682598dba56cd4ccfd17f1bd6`) | `56493fc078c6fc680a5cda3bb50d63b9df04d197b0cf5f03b54a1a2bc666ecaa` | neutral，rejected |
| exp42 | [`cuda_case11_bf16_normalized_partial.cpp`](cuda_case11_bf16_normalized_partial.cpp) | exp36 (`eab62e0e84f538ac75ff0bda8835349f3f8c9c3682598dba56cd4ccfd17f1bd6`) | `f37a49726c8354cda8bf4a4975ba90dbaf880e272c014008b81444b9bac2bf38` | rejected |
| exp43 | [`cuda_case11_bf16_raw_partial.cpp`](cuda_case11_bf16_raw_partial.cpp) | exp42 (`f37a49726c8354cda8bf4a4975ba90dbaf880e272c014008b81444b9bac2bf38`) | `37a94818dfb7d927a9a0783791e81be64f7cb630cc1cf064d4ee8a65681d63df` | rejected |
| exp44 | [`cuda_case8_bf16_raw_partial.cpp`](cuda_case8_bf16_raw_partial.cpp) | exp36 (`eab62e0e84f538ac75ff0bda8835349f3f8c9c3682598dba56cd4ccfd17f1bd6`) | `45e0c8c79219ba2576aea5bd7c96e96825ed110bb5a4fa1f3023ba1c039fd918` | rejected |
| exp46 | [`cuda_case14_mma_f32_warp64_v1.cpp`](cuda_case14_mma_f32_warp64_v1.cpp) | exp36 (`eab62e0e84f538ac75ff0bda8835349f3f8c9c3682598dba56cd4ccfd17f1bd6`) | `de1b4559592d9abeb9970139c4619bd8328354ab84df3136a77a308d16732244` | correct，rejected |
| exp47 | [`cuda_case14_mma_f32_token_parallel_v2.cpp`](cuda_case14_mma_f32_token_parallel_v2.cpp) | exp46 (`de1b4559592d9abeb9970139c4619bd8328354ab84df3136a77a308d16732244`) | `0ba220024c598724c0945d8f935ee6164a5e0158aaf794032d52046ffa1fb76e` | correct，rejected |
| exp48 | [`cuda_case14_mma_f32_bsm_pipeline_v3.cpp`](cuda_case14_mma_f32_bsm_pipeline_v3.cpp) | exp46 (`de1b4559592d9abeb9970139c4619bd8328354ab84df3136a77a308d16732244`) | `ac59f3760835c93b3d8ff5376640189b8235109ccfd1cc53dc0778a2b54f3e47` | correct，rejected |
| exp49 | [`cuda_case14_mma_f32_wave_headpair_exp49.cpp`](cuda_case14_mma_f32_wave_headpair_exp49.cpp) | exp36 (`eab62e0e84f538ac75ff0bda8835349f3f8c9c3682598dba56cd4ccfd17f1bd6`) | `87ae7ccef35d149b4a73bf78bc7d2179e3485ba25d14a76daa8b480e9e12589e` | correct，rejected |
| exp50 | [`cuda_case14_mma_f32_qk_pv_exp50.cpp`](cuda_case14_mma_f32_qk_pv_exp50.cpp) | exp49 (`87ae7ccef35d149b4a73bf78bc7d2179e3485ba25d14a76daa8b480e9e12589e`) | `750f53501164ff5bb8fdee542842e94b6352092ac43fdc87fde49948c6e993cf` | correct，rejected |
| exp51 | [`cuda_case14_split275_exp51.cpp`](cuda_case14_split275_exp51.cpp) | exp36 (`eab62e0e84f538ac75ff0bda8835349f3f8c9c3682598dba56cd4ccfd17f1bd6`) | `2280bbad9bc8560a46e8fe4ab76f348a8ec6eb18a33b7a0efecccc8c1fea477d` | rejected |
| exp52 | [`cuda_case14_int8_normalized_partial_exp52.cpp`](cuda_case14_int8_normalized_partial_exp52.cpp) | exp36 (`eab62e0e84f538ac75ff0bda8835349f3f8c9c3682598dba56cd4ccfd17f1bd6`) | `243604528b397a23a7d0d746ae1acdf0a25c21e1d4f96977fab4b425638b6b56` | correct，rejected |
| exp53 | [`cuda_case11_headpair_bsm_exp53.cpp`](cuda_case11_headpair_bsm_exp53.cpp) | exp36 (`eab62e0e84f538ac75ff0bda8835349f3f8c9c3682598dba56cd4ccfd17f1bd6`) | `17295dfb0f8abcbcfaf734edfbfa450cc3dc9d66adfecfde47f3d16fcba7f46e` | correct full，neutral/rejected |
| exp54 | [`cuda_case14_two_head_bf16_reducer_exp54.cpp`](cuda_case14_two_head_bf16_reducer_exp54.cpp) | exp36 (`eab62e0e84f538ac75ff0bda8835349f3f8c9c3682598dba56cd4ccfd17f1bd6`) | `b1ff372b5139a2d436870fd26db4841bef4d00d339d0f536d330430f1db25aab` | correct full，neutral/rejected |
| exp55 | [`cuda_case14_z1_chunk4_exp55.cpp`](cuda_case14_z1_chunk4_exp55.cpp) | exp36 (`eab62e0e84f538ac75ff0bda8835349f3f8c9c3682598dba56cd4ccfd17f1bd6`) | `a3e7fe4454d624cfaaf3af51ae9bc5e9407870bc758396ace85997e9d25058ff` | correct full，rejected |
| exp56 | [`cuda_case8_headpair_bsm_exp56.cpp`](cuda_case8_headpair_bsm_exp56.cpp) | exp36 (`eab62e0e84f538ac75ff0bda8835349f3f8c9c3682598dba56cd4ccfd17f1bd6`) | `c5f57a2d23d1b99cedfb45114448e3c6e4522c343f579205456353ecc2a7cc1a` | positive，已被 exp57 取代 |
| exp57 | [`cuda_headpair_wave_barrier_exp57.cpp`](cuda_headpair_wave_barrier_exp57.cpp) | exp56 (`c5f57a2d23d1b99cedfb45114448e3c6e4522c343f579205456353ecc2a7cc1a`) | `46a3952188a27f346989015a75cbf12328274de00154660e76a591fc8f8edda5` | positive，已被 exp58 取代 |
| exp58 | [`cuda_headpair_sync_ready_wave_exp58.cpp`](cuda_headpair_sync_ready_wave_exp58.cpp) | exp57 (`46a3952188a27f346989015a75cbf12328274de00154660e76a591fc8f8edda5`) | `df34a4176002f9d98575ca8630dc86ce9f6fae269328189be986e857722ffdc8` | positive，已被 exp61 取代 |
| exp59 | [`cuda_headpair_shared_barrier_exp59.cpp`](cuda_headpair_shared_barrier_exp59.cpp) | exp58 (`df34a4176002f9d98575ca8630dc86ce9f6fae269328189be986e857722ffdc8`) | `3f0a460caaa293742c8c0d98e5d7a9feafbbfc8fccdc19368c99316247273c3f` | correct，neutral/rejected |
| exp60 | [`cuda_kv8_wave_barrier_exp60.cpp`](cuda_kv8_wave_barrier_exp60.cpp) | exp58 (`df34a4176002f9d98575ca8630dc86ce9f6fae269328189be986e857722ffdc8`) | `63d16579dd0e139f1fc3689e288914f40923352c50fd69f3b427542ac836eb92` | positive，已被 exp61 取代 |
| exp61 | [`cuda_kv8_wave_barrier_isolated_exp61.cpp`](cuda_kv8_wave_barrier_isolated_exp61.cpp) | exp60 (`63d16579dd0e139f1fc3689e288914f40923352c50fd69f3b427542ac836eb92`) | `f43f4aa0d5090f06a57e8c7cb119398453f628dba42e795d1b3852301b30df37` | positive，已被 exp62 取代 |
| exp62 | [`cuda_case4_bsm_wave_barrier_exp62.cpp`](cuda_case4_bsm_wave_barrier_exp62.cpp) | exp61 (`f43f4aa0d5090f06a57e8c7cb119398453f628dba42e795d1b3852301b30df37`) | `badab6023d97ded3faa2a125c12fa23f3955b9bcc0b6c8bb3b1d6acf055d9a19` | positive，已被 exp68 取代 |
| exp63 | [`cuda_case14_headpair_wave_bf16_exp63.cpp`](cuda_case14_headpair_wave_bf16_exp63.cpp) | exp62 (`badab6023d97ded3faa2a125c12fa23f3955b9bcc0b6c8bb3b1d6acf055d9a19`) | `b00b455f3c9cbe3961be15022ce9d1ccd2b7e13c65a0481336bee45d9f3af7d1` | correct full，rejected |
| exp64a | [`cuda_case14_direct_q_dynamic_exp64a.cpp`](cuda_case14_direct_q_dynamic_exp64a.cpp) | exp62 (`badab6023d97ded3faa2a125c12fa23f3955b9bcc0b6c8bb3b1d6acf055d9a19`) | `2b1ab720693aabccb96a9b8ea9c32ef6d02f0bec0d170f9953f50d767d47184b` | correct full，rejected |
| exp64b | [`cuda_case14_direct_q_nodyn_exp64b.cpp`](cuda_case14_direct_q_nodyn_exp64b.cpp) | exp64a (`2b1ab720693aabccb96a9b8ea9c32ef6d02f0bec0d170f9953f50d767d47184b`) | `8e6b5899224ee56a73e40fa5c4bb9cadf8666b582716f10cefef59339993d821` | correct full，rejected |
| exp65 | [`cuda_case10_bf16_normalized_partial_exp65.cpp`](cuda_case10_bf16_normalized_partial_exp65.cpp) | exp62 (`badab6023d97ded3faa2a125c12fa23f3955b9bcc0b6c8bb3b1d6acf055d9a19`) | `d19fa936477f321e3b213f9863248b1c660377ce4a5b6b1ce67355057e868a4c` | correct full，rejected |
| exp66 | [`cuda_case6_bsm_wave_exp66.cpp`](cuda_case6_bsm_wave_exp66.cpp) | exp62 (`badab6023d97ded3faa2a125c12fa23f3955b9bcc0b6c8bb3b1d6acf055d9a19`) | `0c97d91a1d803efa0fb528b6e0ebee3e6403056b68cfff7e2f2468af74bf3d46` | correct full，rejected |
| exp67 | [`cuda_case14_headpair_z2_wave_bf16_exp67.cpp`](cuda_case14_headpair_z2_wave_bf16_exp67.cpp) | exp62 (`badab6023d97ded3faa2a125c12fa23f3955b9bcc0b6c8bb3b1d6acf055d9a19`) | `fd1c9bba511ce84388232acca8bba5aaff1857acca4fa4e88078cb0586fd56af` | correct full，rejected |
| exp68 | [`cuda_case14_raw_bperm_qk_exp68.cpp`](cuda_case14_raw_bperm_qk_exp68.cpp) | exp62 (`badab6023d97ded3faa2a125c12fa23f3955b9bcc0b6c8bb3b1d6acf055d9a19`) | `cbd8d4ea88eb2c4d7561bd3e67894aa09459dad7c23e6c5f5df31ff02c029f4a` | positive，已被 exp69 取代 |
| exp69 | [`cuda_case10_raw_bperm_qk_exp69.cpp`](cuda_case10_raw_bperm_qk_exp69.cpp) | exp68 (`cbd8d4ea88eb2c4d7561bd3e67894aa09459dad7c23e6c5f5df31ff02c029f4a`) | `bbb0ede409a4833d7fe7495102d0d50eff9cb7c443732afec5760a0f9ebedde8` | positive，已被 exp70 取代 |
| exp70 | [`cuda_case5_raw_bperm_qk_exp70.cpp`](cuda_case5_raw_bperm_qk_exp70.cpp) | exp69 (`bbb0ede409a4833d7fe7495102d0d50eff9cb7c443732afec5760a0f9ebedde8`) | `9cf8b0680062fa124922e0dc900ac702dc0edb384e364fc17c29e897fd98d49a` | positive，已被 exp71 取代 |
| exp71 | [`cuda_case11_headpair_raw_bperm_qk_exp71.cpp`](cuda_case11_headpair_raw_bperm_qk_exp71.cpp) | exp70 (`9cf8b0680062fa124922e0dc900ac702dc0edb384e364fc17c29e897fd98d49a`) | `61661232512d4fa11f1d133c3f2289eeded1e9d62bb03ba04ca26a704c1013a5` | positive，已被 exp72 取代 |
| exp72 | [`cuda_case9_raw_bperm_qk_exp72.cpp`](cuda_case9_raw_bperm_qk_exp72.cpp) | exp71 (`61661232512d4fa11f1d133c3f2289eeded1e9d62bb03ba04ca26a704c1013a5`) | `c06c332f753002149d19c324f569ae07209b842d84af2388f7a3b90f6173ba76` | positive，已被 exp73 取代 |
| exp73 | [`cuda_case7_raw_bperm_qk_exp73.cpp`](cuda_case7_raw_bperm_qk_exp73.cpp) | exp72 (`c06c332f753002149d19c324f569ae07209b842d84af2388f7a3b90f6173ba76`) | `454e74c6a7ddded7357909c822feb0df03c19a5c963f1371026a75b1fdf08fd9` | positive，已被 exp74 取代 |
| exp74 | [`cuda_case12_raw_bperm_qk_exp74.cpp`](cuda_case12_raw_bperm_qk_exp74.cpp) | exp73 (`454e74c6a7ddded7357909c822feb0df03c19a5c963f1371026a75b1fdf08fd9`) | `9da260120c01d2a0e72beac9dcf4d091aff8bec2ae928bd6405614daafafac1f` | positive，已被 exp75 取代 |
| exp75 | [`cuda_case13_raw_bperm_qk_exp75.cpp`](cuda_case13_raw_bperm_qk_exp75.cpp) | exp74 (`9da260120c01d2a0e72beac9dcf4d091aff8bec2ae928bd6405614daafafac1f`) | `07cb13baf9b8b99ec32852086f7447b5dc3ab6d81dd642b7f8fddb5120855bab` | positive，已被 exp76 取代 |
| exp76 | [`cuda_case8_headpair_raw_bperm_qk_exp76.cpp`](cuda_case8_headpair_raw_bperm_qk_exp76.cpp) | exp75 (`07cb13baf9b8b99ec32852086f7447b5dc3ab6d81dd642b7f8fddb5120855bab`) | `af8f6a894ad4802b44b666b5b17caf7a74f7df3a93a37b2001edd9a499de65f9` | positive，已被 exp77 取代 |
| exp77 | [`cuda_case4_raw_bperm_qk_exp77.cpp`](cuda_case4_raw_bperm_qk_exp77.cpp) | exp76 (`af8f6a894ad4802b44b666b5b17caf7a74f7df3a93a37b2001edd9a499de65f9`) | `2529e6e4e9467bb815f95d2d6b898565ca2dc28376ace82eea3e9a2400ead993` | positive，已被 exp78 取代 |
| exp78 | [`cuda_case6_raw_bperm_qk_exp78.cpp`](cuda_case6_raw_bperm_qk_exp78.cpp) | exp77 (`2529e6e4e9467bb815f95d2d6b898565ca2dc28376ace82eea3e9a2400ead993`) | `6e2d3473cc90bc0b0c45ba143e21c5153b094a2b5ffcf52ac6df55456211e9df` | positive，已被 exp79 取代 |
| exp79 | [`cuda_case3_raw_bperm_qk_exp79.cpp`](cuda_case3_raw_bperm_qk_exp79.cpp) | exp78 (`6e2d3473cc90bc0b0c45ba143e21c5153b094a2b5ffcf52ac6df55456211e9df`) | `5eccfc50acd46b1b416dd9157c930a4c6a20d92fd33010a8e725fffb82b4f973` | positive，已被 exp87 取代 |
| exp80 | [`cuda_case11_headpair_combined_exp80.cpp`](cuda_case11_headpair_combined_exp80.cpp) | exp79 (`5eccfc50acd46b1b416dd9157c930a4c6a20d92fd33010a8e725fffb82b4f973`) | `5cf52f0f08214abbfb05bcf391f3e9c27152e4b5414ae8a6b8040a7987cc8e1e` | correct，rejected（case11约慢11.3%） |
| exp81 | [`cuda_case11_head4_z4_exp81.cpp`](cuda_case11_head4_z4_exp81.cpp) | exp79 (`5eccfc50acd46b1b416dd9157c930a4c6a20d92fd33010a8e725fffb82b4f973`) | `b18f76770f2097adbd981422dbb3d0887bbd47bd5879e9d9a4e3b3076075cd43` | correct full，rejected（消偏后约慢0.32%） |
| exp82 | [`cuda_case11_head4_z4_fp16score_exp82.cpp`](cuda_case11_head4_z4_fp16score_exp82.cpp) | exp81 (`b18f76770f2097adbd981422dbb3d0887bbd47bd5879e9d9a4e3b3076075cd43`) | `a9f5666a6dd80b9ee6a16eb890fa3a93ee74b3b2f179adf5bf5c9fb029e68824` | correct full，rejected（约慢9.35%） |
| exp83 | [`cuda_case11_head4_z4_packedq_exp83.cpp`](cuda_case11_head4_z4_packedq_exp83.cpp) | exp81 (`b18f76770f2097adbd981422dbb3d0887bbd47bd5879e9d9a4e3b3076075cd43`) | `c126d73918567df42c9945aa729acb0614a642d5f42770b1ac0ddf2101ada31a` | correct full，neutral/rejected |
| exp84 | [`cuda_case11_head4_z4_dimmajor_exp84.cpp`](cuda_case11_head4_z4_dimmajor_exp84.cpp) | exp83 (`c126d73918567df42c9945aa729acb0614a642d5f42770b1ac0ddf2101ada31a`) | `0463aea9c0cb42ab7f11468c791878f776fded1f24509b8a38a6cb7dc589bb24` | correct full，rejected（约慢3.38%） |
| exp85 | [`cuda_case11_head4_z4_sharedq_dimmajor_exp85.cpp`](cuda_case11_head4_z4_sharedq_dimmajor_exp85.cpp) | exp84 (`0463aea9c0cb42ab7f11468c791878f776fded1f24509b8a38a6cb7dc589bb24`) | `cd340bdaaa25a0c58f707925437e958499838864a66053a2d82d972a10b563c3` | correct full，rejected（约慢17.78%） |
| exp86 | [`cuda_case10_group8_reduce128_exp86.cpp`](cuda_case10_group8_reduce128_exp86.cpp) | exp79 (`5eccfc50acd46b1b416dd9157c930a4c6a20d92fd33010a8e725fffb82b4f973`) | `56eb1fb927339bf9ed0bfb6cb820c83d19017b32698d61877f736ca8a0d09ec3` | correct full，rejected（约慢13.4%） |
| exp87 | [`cuda_case10_vec4_reduce128_exp87.cpp`](cuda_case10_vec4_reduce128_exp87.cpp) | exp79 (`5eccfc50acd46b1b416dd9157c930a4c6a20d92fd33010a8e725fffb82b4f973`) | `6c1de4a3736dd6b565ab515a0ad3c5b5cdc3650b79a97c2458145c49769173a6` | positive，已被 exp88 取代 |
| exp88 | [`cuda_case8_vec4_reduce49_exp88.cpp`](cuda_case8_vec4_reduce49_exp88.cpp) | exp87 (`6c1de4a3736dd6b565ab515a0ad3c5b5cdc3650b79a97c2458145c49769173a6`) | `e368f80dbc47d5ebc485a1eea1fc4f33e924e83e00521110fcbf8e0efbd41293` | positive，已被 exp89 取代 |
| exp89 | [`cuda_case11_vec4_reduce49_exp89.cpp`](cuda_case11_vec4_reduce49_exp89.cpp) | exp88 (`e368f80dbc47d5ebc485a1eea1fc4f33e924e83e00521110fcbf8e0efbd41293`) | `b4333f5c069292ccc9755adc616769a56872645163883aa45f2ec3c4d2bce25a` | positive，已被 exp91 取代 |
| exp90 | [`cuda_case13_vec4_reduce257_exp90.cpp`](cuda_case13_vec4_reduce257_exp90.cpp) | exp89 (`b4333f5c069292ccc9755adc616769a56872645163883aa45f2ec3c4d2bce25a`) | `eb0384b2843a21c74674386af9954a58acdb9be9dcffd6174fca8d5b8ba7125f` | correct full，rejected（约慢 1.05%） |
| exp91 | [`cuda_case12_vec4_reduce129_exp91.cpp`](cuda_case12_vec4_reduce129_exp91.cpp) | exp89 (`b4333f5c069292ccc9755adc616769a56872645163883aa45f2ec3c4d2bce25a`) | `de9bc8c3c947134990e83069e7b13e934be0ddc6a40c1696664c00b2777faf90` | positive，已被 exp92 取代 |
| exp92 | [`cuda_case9_vec4_reduce25_exp92.cpp`](cuda_case9_vec4_reduce25_exp92.cpp) | exp91 (`de9bc8c3c947134990e83069e7b13e934be0ddc6a40c1696664c00b2777faf90`) | `84537ed7319d03d0cd46171d126cc819d0b7a15d744e259339facd6dfe729f86` | positive，已被 exp94 取代 |
| exp93 | [`cuda_case7_vec4_reduce15_exp93.cpp`](cuda_case7_vec4_reduce15_exp93.cpp) | exp92 (`84537ed7319d03d0cd46171d126cc819d0b7a15d744e259339facd6dfe729f86`) | `fdc6c8ef03b5e1a10cbc906792d64afce594df4627c1f04207c19c451344c66e` | correct full，rejected（约慢 0.26%） |
| exp94 | [`cuda_case13_vec2_reduce257_exp94.cpp`](cuda_case13_vec2_reduce257_exp94.cpp) | exp92 (`84537ed7319d03d0cd46171d126cc819d0b7a15d744e259339facd6dfe729f86`) | `441da88b5fd4e2e26495be0047e1be4a0c425dd6ac7d7ce84c76a8ed6e7dfeec` | positive，已被 exp103 取代 |
| exp95 | [`cuda_case11_pid_prefetch_exp95.cpp`](cuda_case11_pid_prefetch_exp95.cpp) | exp94 (`441da88b5fd4e2e26495be0047e1be4a0c425dd6ac7d7ce84c76a8ed6e7dfeec`) | `bf1b613c2f7686d3e90af10ef1af7d87954c5b1c1f436b0c433df7e826dd073e` | correct full，rejected（约慢 0.58%） |
| exp96 | [`cuda_case11_headpair_packedq_exp96.cpp`](cuda_case11_headpair_packedq_exp96.cpp) | exp94 (`441da88b5fd4e2e26495be0047e1be4a0c425dd6ac7d7ce84c76a8ed6e7dfeec`) | `67dce5a3814f3949b5110cb37ee42cfe1c2bfdcb47758a7286a54eea11be9e8b` | resource-gate rejected（full资源不变） |
| exp97 | [`cuda_case11_wave_broadcast_k_exp97.cpp`](cuda_case11_wave_broadcast_k_exp97.cpp) | exp94 (`441da88b5fd4e2e26495be0047e1be4a0c425dd6ac7d7ce84c76a8ed6e7dfeec`) | `125b7f31f3066ea9e6ea419a6baf895791431db717ec2f7ace091fa536fb9a14` | correct full，rejected（约慢41.3%） |
| exp98 | [`cuda_case11_head4_pairwise_exp98.cpp`](cuda_case11_head4_pairwise_exp98.cpp) | exp94 (`441da88b5fd4e2e26495be0047e1be4a0c425dd6ac7d7ce84c76a8ed6e7dfeec`) | `25dc89019e7eb6417c964cb07957bc17d5db900bf2b56d334130e0dd1cc4ed25` | resource-gate rejected（140 MTreg/3 warps） |
| exp99 | [`cuda_case10_single_full_exp99.cpp`](cuda_case10_single_full_exp99.cpp) | exp94 (`441da88b5fd4e2e26495be0047e1be4a0c425dd6ac7d7ce84c76a8ed6e7dfeec`) | `87174eea31dcb7a1d078da80bc7954184d3ddb42c270a7832f7ca37f5d3bc7a2` | diagnostic，boundary错误/rejected |
| exp100 | [`cuda_case14_separate_tail_exp100.cpp`](cuda_case14_separate_tail_exp100.cpp) | exp94 (`441da88b5fd4e2e26495be0047e1be4a0c425dd6ac7d7ce84c76a8ed6e7dfeec`) | `8d8e0f995271c08a827550abf40c9f54a55521eb9784c18876d07b4a33f81193` | correct target，rejected（约慢1.60%） |
| exp101 | [`cuda_case14_fused_tail_reduce_exp101.cpp`](cuda_case14_fused_tail_reduce_exp101.cpp) | exp94 (`441da88b5fd4e2e26495be0047e1be4a0c425dd6ac7d7ce84c76a8ed6e7dfeec`) | `51df69110f7576e6c6c0c4840e209a14baf486006fa7f00363b53ba834748e9b` | correct target，rejected（约慢0.92%） |
| exp102 | [`cuda_case14_direct_tail_reduce_exp102.cpp`](cuda_case14_direct_tail_reduce_exp102.cpp) | exp101 (`51df69110f7576e6c6c0c4840e209a14baf486006fa7f00363b53ba834748e9b`) | `a54eaa06603260dbb9e56778ba5a389a1e9cda4d112256e273d3ebcbcbcfacfb` | correct full，neutral/rejected |
| exp103 | [`cuda_case14_last_split_tail_exp103.cpp`](cuda_case14_last_split_tail_exp103.cpp) | exp94 (`441da88b5fd4e2e26495be0047e1be4a0c425dd6ac7d7ce84c76a8ed6e7dfeec`) | `3830789e9c960591f2544ba6991de3c69ad3039429107503be99f803c33aa3c3` | 性能positive，但split模数边界错误，已由exp103b修复 |
| exp103b | [`cuda_case14_fused_tail_live_count_exp103b.cpp`](cuda_case14_fused_tail_live_count_exp103b.cpp) | exp103 (`3830789e9c960591f2544ba6991de3c69ad3039429107503be99f803c33aa3c3`) | `1864bb1c7be47f61dfb8560afd46b981dd77292756afcb52113a43c0108152f8` | correctness修复且性能中性，已被exp104取代 |
| exp104 | [`cuda_case13_last_split_tail_exp104.cpp`](cuda_case13_last_split_tail_exp104.cpp) | exp103b (`1864bb1c7be47f61dfb8560afd46b981dd77292756afcb52113a43c0108152f8`) | `62f9ec33f55b228b961177299d7c1144a5f865dfd7e69eed2e0cff0fcdcef6a8` | positive，已被exp105取代 |
| exp105 | [`cuda_case11_last_split_tail_exp105.cpp`](cuda_case11_last_split_tail_exp105.cpp) | exp104 (`62f9ec33f55b228b961177299d7c1144a5f865dfd7e69eed2e0cff0fcdcef6a8`) | `f52f0b9452b9588da661610ba4178b34c51bc6a3a938b9dd6a2753dd94103dc4` | positive，已被exp106取代 |
| exp106 | [`cuda_case8_last_split_tail_exp106.cpp`](cuda_case8_last_split_tail_exp106.cpp) | exp105 (`f52f0b9452b9588da661610ba4178b34c51bc6a3a938b9dd6a2753dd94103dc4`) | `f5b0fd660e97b94095296769823bbf3120df5c8c3331b1c422ad4b709aabcffb` | positive，已被exp107取代 |
| exp107 | [`cuda_case9_last_split_tail_exp107.cpp`](cuda_case9_last_split_tail_exp107.cpp) | exp106 (`f5b0fd660e97b94095296769823bbf3120df5c8c3331b1c422ad4b709aabcffb`) | `51337fb6f0885ab41eea3a730f61970150db55790df562774d8c3b2a74444855` | positive，已被exp108取代 |
| exp108 | [`cuda_case7_last_split_tail_exp108.cpp`](cuda_case7_last_split_tail_exp108.cpp) | exp107 (`51337fb6f0885ab41eea3a730f61970150db55790df562774d8c3b2a74444855`) | `9b67b66fb94987c634143ca39e1970f833c524bd021f6af633b3ffd63a2c3454` | positive，已被exp109取代 |
| exp109 | [`cuda_case12_empty_tail_exp109.cpp`](cuda_case12_empty_tail_exp109.cpp) | exp108 (`9b67b66fb94987c634143ca39e1970f833c524bd021f6af633b3ffd63a2c3454`) | `a4185589ccf01ac01485cb9ee1d26b9f28043d24d343dde0ba9402d8cef81718` | positive，已被exp110取代 |
| exp110 | [`cuda_case11_register_prefetch_exp110.cpp`](cuda_case11_register_prefetch_exp110.cpp) | exp109 (`a4185589ccf01ac01485cb9ee1d26b9f28043d24d343dde0ba9402d8cef81718`) | `5500309e3a17cc3c8cab8eceecb7ba8d1ac7fa6b661a0971adf55cd6bcc16a81` | positive，已被exp112取代 |
| exp111 | [`cuda_case12_k_register_prefetch_exp111.cpp`](cuda_case12_k_register_prefetch_exp111.cpp) | exp110 (`5500309e3a17cc3c8cab8eceecb7ba8d1ac7fa6b661a0971adf55cd6bcc16a81`) | `7f34d8c706a6354bcacc3de496b9dbd80e0467c8ce6945a5795553c46d7505b1` | resource-gate rejected（32 B stack spill） |
| exp112 | [`cuda_case8_sync_register_prefetch_exp112.cpp`](cuda_case8_sync_register_prefetch_exp112.cpp) | exp110 (`5500309e3a17cc3c8cab8eceecb7ba8d1ac7fa6b661a0971adf55cd6bcc16a81`) | `867deaf62ae2767831451fb94a0c51273b2456a525fb87137cbefdc347a5de20` | positive，已被exp114取代 |
| exp113 | [`cuda_case11_k_only_register_prefetch_exp113.cpp`](cuda_case11_k_only_register_prefetch_exp113.cpp) | exp112 (`867deaf62ae2767831451fb94a0c51273b2456a525fb87137cbefdc347a5de20`) | `3f339244e6c6c4a7df3c305b5b76004f18d3e578fc4e82bb648c1ed581e7277d` | rejected（case11约慢3.20%） |
| exp114 | [`cuda_case11_early_pid_prefetch_exp114.cpp`](cuda_case11_early_pid_prefetch_exp114.cpp) | exp112 (`867deaf62ae2767831451fb94a0c51273b2456a525fb87137cbefdc347a5de20`) | `c0b50cf2523b1b5439aa3fd128f0dc44a043b7ea29581f3ad005f433269b5409` | positive，已被exp115取代 |
| exp115 | [`cuda_case8_early_pid_prefetch_exp115.cpp`](cuda_case8_early_pid_prefetch_exp115.cpp) | exp114 (`c0b50cf2523b1b5439aa3fd128f0dc44a043b7ea29581f3ad005f433269b5409`) | `b73fb54d9457d7bf2d02649a33a394669af965a9956b34ae57d46f68017e02d6` | positive，当前本地候选基线 |
| exp116 | [`cuda_case11_pipelined_pid_exp116.cpp`](cuda_case11_pipelined_pid_exp116.cpp) | exp115 (`b73fb54d9457d7bf2d02649a33a394669af965a9956b34ae57d46f68017e02d6`) | `8673c1fbf5ed1620560b634b3bfcb7ba5a7ff16f2ecdb3e662e494f0f376f61e` | rejected（case11约慢1.12%） |

exp45 的原生 FP32 MMA runtime fragment/精度探针已闭合，源码位于 `tests/archive/closed-backend-probes/c500_mma_f32_fragment_probe.cpp` 和 `tests/archive/closed-backend-probes/c500_mma_f32_fragment_probe.py`，不属于可提交 solution；完整映射、精度与运行证据见根目录 `notes.md`。

## 组合主链

后半段组合实验的源码关系为：

```text
#106626 bc5b3a4d...
  -> exp17 fb2e0ca4...  (case 8 head-pair/z4)
  -> exp18 445e7046...  (+ case 11 split48)
  -> exp20 42cb6e43...  (+ case 14 split257)
  -> exp22 e4827a65...  (+ case 5 split5)
  -> exp35 c8678887...  (+ head-pair direct Q)
  -> exp36 eab62e0e...  (+ case 14 normalized-BF16 partial)
  -> exp56 c5f57a2d...  (+ case 8 head-pair BSM async)
  -> exp57 46a39521...  (+ head-pair page-loop wave barriers)
  -> exp58 df34a417...  (+ sync case 11 page-ready wave barrier)
  -> exp60 63d16579...  (+ sync KV8 token-parallel wave barriers)
  -> exp61 f43f4aa0...  (+ non-target codegen isolation)
  -> exp62 badab602...  (+ case 4 BSM K/V overwrite wave barriers)
  -> exp68 cbd8d4ea...  (+ case 14 raw row16 BSM bpermute QK)
  -> exp69 bbb0ede4...  (+ case 10 raw row16 BSM bpermute QK)
  -> exp70 9cf8b068...  (+ case 5 raw row16 BSM bpermute QK)
  -> exp71 61661232...  (+ case 11 head-pair raw row16 BSM bpermute QK)
  -> exp72 c06c332f...  (+ case 9 KV8 raw row16 BSM bpermute QK)
  -> exp73 454e74c6...  (+ case 7 KV8 raw row16 BSM bpermute QK)
  -> exp74 9da26012...  (+ case 12 KV8 raw row16 BSM bpermute QK)
  -> exp75 07cb13ba...  (+ case 13 KV8 raw row16 BSM bpermute QK)
  -> exp76 af8f6a89...  (+ case 8 head-pair raw row16 BSM bpermute QK)
  -> exp77 2529e6e4...  (+ case 4 KV8 raw row16 BSM bpermute QK)
  -> exp78 6e2d3473...  (+ case 6 KV8 raw row16 BSM bpermute QK)
  -> exp79 5eccfc50...  (+ case 3 KV4 raw row16 BSM bpermute QK)
  -> exp87 6c1de4a3...  (+ case 10 32-thread vec4 reducer)
  -> exp88 e368f80d...  (+ case 8 32-thread vec4 reducer)
  -> exp89 b4333f5c...  (+ case 11 32-thread vec4 reducer)
  -> exp91 de9bc8c3...  (+ case 12 32-thread vec4 reducer)
  -> exp92 84537ed7...  (+ case 9 32-thread vec4 reducer)
  -> exp94 441da88b...  (+ case 13 64-thread vec2 reducer)
  -> exp103  3830789e...  (+ case 14 underfilled last-split tail fusion；原reducer模数边界有误)
  -> exp103b 1864bb1c...  (+ fused-tail live-split correctness修复)
  -> exp104  62f9ec33...  (+ case 13 underfilled last-split tail fusion)
  -> exp105  f52f0b94...  (+ case 11 head-pair/z4 underfilled last-split tail fusion)
  -> exp106  f5b0fd66...  (+ case 8 BSM head-pair/z4 last-split tail fusion / empty-tail launch removal)
  -> exp107  51337fb6...  (+ case 9 KV8 last-split tail fusion / empty-tail launch removal)
  -> exp108  9b67b66f...  (+ case 7 KV8 last-split tail fusion / group8 fused live-count)
  -> exp109  a4185589...  (+ case 12 KV8 empty-tail launch/129th partial removal)
  -> exp110  5500309e...  (+ case 11 sync K/V register lookahead / one fewer wave barrier)
  -> exp112  867deaf6...  (+ case 8 sync K/V register lookahead，替换BSM loader)
  -> exp114  c0b50cf2...  (+ case 11 register-lookahead提前解析next page ID)
  -> exp115  b73fb54d...  (+ case 8 register-lookahead提前解析next page ID)
```

exp19、exp21、exp23–exp34、exp37–exp55、exp59、exp63–67、exp80–86、exp90、exp93、exp95–102、exp111、exp113、exp116 均为从相应主链节点分叉的诊断或失败候选，不属于最终组合链；exp115 是当前正确主链末端，但尚未经过 OJ 判定。原始exp103不得单独作为control。
