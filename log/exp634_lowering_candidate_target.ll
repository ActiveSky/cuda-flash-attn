define protected metaxgpu_kernel void @_Z32paged_decode_single_token_kernelILi4ELi8EEvPK15__maca_bfloat16PS0_PKii(ptr addrspace(4) noalias nocapture noundef %0, ptr addrspace(1) noalias nocapture noundef %1, ptr addrspace(1) noalias nocapture noundef readonly %2, i32 noundef %3) local_unnamed_addr #7 comdat {
  %5 = tail call noundef range(i32 0, 1024) i32 @llvm.mxc.thread.id.x(), !range !27
  %6 = icmp ugt i32 %5, 15
  br i1 %6, label %51, label %7

7:                                                ; preds = %4
  %8 = tail call noundef range(i32 0, 2147483647) i32 @llvm.mxc.block.id.x(), !range !16
  %9 = lshr i32 %8, 2
  %10 = mul nsw i32 %9, %3
  %11 = sext i32 %10 to i64
  %12 = getelementptr inbounds i32, ptr addrspace(1) %2, i64 %11
  %13 = load i32, ptr addrspace(1) %12, align 4, !tbaa !17
  %14 = shl i32 %13, 13
  %15 = shl i32 %8, 7
  %16 = and i32 %15, 384
  %17 = or disjoint i32 %14, %16
  %18 = sext i32 %17 to i64
  %19 = getelementptr inbounds %struct.__maca_bfloat16.1, ptr addrspace(4) %0, i64 %18
  %20 = shl nuw nsw i32 %5, 4
  %21 = zext nneg i32 %20 to i64
  %22 = getelementptr inbounds i8, ptr addrspace(4) %19, i64 %21
  %23 = addrspacecast ptr addrspace(4) %22 to ptr addrspace(1)
  %24 = tail call noundef <4 x i32> @llvm.mxc.ldg.predicator.v4i32(ptr addrspace(1) %23, i32 0, i64 -1, i1 true, i1 true, i1 false, i1 false), !call_argsrelate !35
  %25 = shl i32 %8, 10
  %26 = getelementptr inbounds i8, ptr addrspace(1) %1, i64 %21
  %27 = zext i32 %25 to i64
  %28 = getelementptr inbounds %struct.__maca_bfloat16.1, ptr addrspace(1) %26, i64 %27
  %29 = tail call i64 @llvm.mxc.icmp.i64.i32(i32 1, i32 1, i32 32) #25
  tail call void @llvm.mxc.stg.predicator.v4i32(ptr addrspace(1) %28, i32 0, <4 x i32> %24, i64 %29, i1 true, i1 false, i1 false), !call_argsrelate !36
  %30 = or disjoint i64 %27, 128
  %31 = getelementptr inbounds %struct.__maca_bfloat16.1, ptr addrspace(1) %26, i64 %30
  %32 = tail call i64 @llvm.mxc.icmp.i64.i32(i32 1, i32 1, i32 32) #25
  tail call void @llvm.mxc.stg.predicator.v4i32(ptr addrspace(1) %31, i32 0, <4 x i32> %24, i64 %32, i1 true, i1 false, i1 false), !call_argsrelate !36
  %33 = or disjoint i64 %27, 256
  %34 = getelementptr inbounds %struct.__maca_bfloat16.1, ptr addrspace(1) %26, i64 %33
  %35 = tail call i64 @llvm.mxc.icmp.i64.i32(i32 1, i32 1, i32 32) #25
  tail call void @llvm.mxc.stg.predicator.v4i32(ptr addrspace(1) %34, i32 0, <4 x i32> %24, i64 %35, i1 true, i1 false, i1 false), !call_argsrelate !36
  %36 = or disjoint i64 %27, 384
  %37 = getelementptr inbounds %struct.__maca_bfloat16.1, ptr addrspace(1) %26, i64 %36
  %38 = tail call i64 @llvm.mxc.icmp.i64.i32(i32 1, i32 1, i32 32) #25
  tail call void @llvm.mxc.stg.predicator.v4i32(ptr addrspace(1) %37, i32 0, <4 x i32> %24, i64 %38, i1 true, i1 false, i1 false), !call_argsrelate !36
  %39 = or disjoint i64 %27, 512
  %40 = getelementptr inbounds %struct.__maca_bfloat16.1, ptr addrspace(1) %26, i64 %39
  %41 = tail call i64 @llvm.mxc.icmp.i64.i32(i32 1, i32 1, i32 32) #25
  tail call void @llvm.mxc.stg.predicator.v4i32(ptr addrspace(1) %40, i32 0, <4 x i32> %24, i64 %41, i1 true, i1 false, i1 false), !call_argsrelate !36
  %42 = or disjoint i64 %27, 640
  %43 = getelementptr inbounds %struct.__maca_bfloat16.1, ptr addrspace(1) %26, i64 %42
  %44 = tail call i64 @llvm.mxc.icmp.i64.i32(i32 1, i32 1, i32 32) #25
  tail call void @llvm.mxc.stg.predicator.v4i32(ptr addrspace(1) %43, i32 0, <4 x i32> %24, i64 %44, i1 true, i1 false, i1 false), !call_argsrelate !36
  %45 = or disjoint i64 %27, 768
  %46 = getelementptr inbounds %struct.__maca_bfloat16.1, ptr addrspace(1) %26, i64 %45
  %47 = tail call i64 @llvm.mxc.icmp.i64.i32(i32 1, i32 1, i32 32) #25
  tail call void @llvm.mxc.stg.predicator.v4i32(ptr addrspace(1) %46, i32 0, <4 x i32> %24, i64 %47, i1 true, i1 false, i1 false), !call_argsrelate !36
  %48 = or disjoint i64 %27, 896
  %49 = getelementptr inbounds %struct.__maca_bfloat16.1, ptr addrspace(1) %26, i64 %48
  %50 = tail call i64 @llvm.mxc.icmp.i64.i32(i32 1, i32 1, i32 32) #25
  tail call void @llvm.mxc.stg.predicator.v4i32(ptr addrspace(1) %49, i32 0, <4 x i32> %24, i64 %50, i1 true, i1 false, i1 false), !call_argsrelate !36
  br label %51

51:                                               ; preds = %7, %4
  ret void
}
