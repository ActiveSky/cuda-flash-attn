define protected metaxgpu_kernel void @_Z32paged_decode_single_token_kernelILi4ELi8EEvPK15__maca_bfloat16PS0_PKii(ptr addrspace(4) noalias nocapture noundef readonly %0, ptr addrspace(1) noalias nocapture noundef writeonly %1, ptr addrspace(1) noalias nocapture noundef readonly %2, i32 noundef %3) local_unnamed_addr #7 comdat {
  %5 = tail call noundef range(i32 0, 1024) i32 @llvm.mxc.thread.id.x(), !range !27
  %6 = icmp ugt i32 %5, 127
  br i1 %6, label %30, label %7

7:                                                ; preds = %4
  %8 = tail call noundef range(i32 0, 2147483647) i32 @llvm.mxc.block.id.x(), !range !16
  %9 = lshr i32 %8, 2
  %10 = and i32 %5, 15
  %11 = mul nsw i32 %9, %3
  %12 = sext i32 %11 to i64
  %13 = getelementptr inbounds i32, ptr addrspace(1) %2, i64 %12
  %14 = load i32, ptr addrspace(1) %13, align 4, !tbaa !17
  %15 = shl i32 %14, 13
  %16 = shl i32 %8, 7
  %17 = and i32 %16, 384
  %18 = or disjoint i32 %15, %17
  %19 = sext i32 %18 to i64
  %20 = getelementptr inbounds %struct.__maca_bfloat16.1, ptr addrspace(4) %0, i64 %19
  %21 = shl i32 %8, 10
  %22 = shl nuw nsw i32 %5, 3
  %23 = and i32 %22, 896
  %24 = or disjoint i32 %23, %21
  %25 = zext nneg i32 %24 to i64
  %26 = getelementptr inbounds %struct.__maca_bfloat16.1, ptr addrspace(1) %1, i64 %25
  %27 = zext nneg i32 %10 to i64
  %28 = getelementptr inbounds %struct.uint4.2, ptr addrspace(4) %20, i64 %27
  %29 = getelementptr inbounds %struct.uint4.2, ptr addrspace(1) %26, i64 %27
  tail call void @llvm.memcpy.p1.p4.i64(ptr addrspace(1) noundef align 16 dereferenceable(16) %29, ptr addrspace(4) noundef align 16 dereferenceable(16) %28, i64 16, i1 false), !tbaa.struct !35, !call_argsrelate !36
  br label %30

30:                                               ; preds = %7, %4
  ret void
}
